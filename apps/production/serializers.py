"""
生产防疫序列化器
================

含饲料、投喂（库存事务）、疫苗、疾病上报等校验逻辑；投喂创建/更新使用 ``select_for_update`` 防止超卖库存。
"""
from django.db import transaction
from django.db.models import F
from django.utils import timezone
from rest_framework import serializers
from .models import FeedInfo, FeedingRecord, VaccinationRecord, DiseaseReport
from apps.livestock.models import LivestockBatch
from apps.core.utils import get_image_upload_error

class FeedInfoSerializer(serializers.ModelSerializer):
    """
    饲料信息序列化器
    """
    farmer_name = serializers.ReadOnlyField(source='farmer.farmer_name')
    
    class Meta:
        model = FeedInfo
        fields = '__all__'
        read_only_fields = ('farmer', 'unit', 'created_at')

    def validate_image(self, value):
        error_msg = get_image_upload_error(value)
        if error_msg:
            raise serializers.ValidationError(error_msg)
        return value

class FeedingRecordSerializer(serializers.ModelSerializer):
    """
    喂养记录序列化器
    """
    feed_name = serializers.ReadOnlyField(source='feed.feed_name')
    feed_unit = serializers.ReadOnlyField(source='feed.unit')
    batch_code = serializers.ReadOnlyField(source='batch.batch_code')
    farmer_name = serializers.ReadOnlyField(source='batch.farmer.farmer_name')
    
    class Meta:
        model = FeedingRecord
        fields = '__all__'

    def validate(self, attrs):
        request = self.context.get('request')
        instance = getattr(self, 'instance', None)

        if instance is not None and 'batch' in attrs and attrs['batch'].id != instance.batch_id:
            raise serializers.ValidationError({'batch': '不允许修改关联批次'})

        feed_weight = attrs.get('feed_weight')
        if feed_weight is not None and feed_weight <= 0:
            raise serializers.ValidationError({'feed_weight': '投喂重量必须大于 0'})

        batch = attrs.get('batch')
        if batch is None and instance is not None:
            batch = instance.batch

        if batch is not None:
            if instance is None:
                if batch.status != 'active':
                    raise serializers.ValidationError({
                        'batch': '该批次已出栏或已结束养殖，无法新增投喂记录',
                    })
            else:
                if batch.status != 'active':
                    feed_changed = 'feed' in attrs and attrs['feed'].pk != instance.feed_id
                    weight_changed = (
                        'feed_weight' in attrs
                        and attrs['feed_weight'] != instance.feed_weight
                    )
                    if feed_changed or weight_changed:
                        raise serializers.ValidationError({
                            'batch': '该批次已出栏，无法修改饲料种类或投喂重量',
                        })

        if request and request.user and request.user.is_authenticated and not request.user.is_staff:
            feed = attrs.get('feed')
            if feed is None and instance is not None:
                feed = instance.feed

            if batch:
                if getattr(batch.farmer, 'user_id', None) != request.user.id:
                    raise serializers.ValidationError({'batch': '无权操作该批次'})
            
            if feed:
                if getattr(feed.farmer, 'user_id', None) != request.user.id:
                    raise serializers.ValidationError({'feed': '无权使用该饲料'})

            if batch and feed and batch.farmer_id != feed.farmer_id:
                raise serializers.ValidationError({'feed': '饲料与批次不属于同一养殖户'})

        return attrs

    def create(self, validated_data):
        feed = validated_data['feed']
        feed_weight = validated_data['feed_weight']
        batch = validated_data['batch']

        with transaction.atomic():
            locked_batch = LivestockBatch.objects.select_for_update().get(pk=batch.pk)
            if locked_batch.status != 'active':
                raise serializers.ValidationError({
                    'batch': '该批次已出栏或已结束养殖，无法新增投喂记录',
                })

            locked_feed = FeedInfo.objects.select_for_update().get(pk=feed.pk)
            if locked_feed.stock_quantity < feed_weight:
                raise serializers.ValidationError({'feed_weight': '饲料库存不足'})

            FeedInfo.objects.filter(pk=locked_feed.pk).update(stock_quantity=F('stock_quantity') - feed_weight)
            return FeedingRecord.objects.create(**validated_data)

    def update(self, instance, validated_data):
        new_feed = validated_data.get('feed', instance.feed)
        new_feed_weight = validated_data.get('feed_weight', instance.feed_weight)

        old_feed_id = instance.feed_id
        old_feed_weight = instance.feed_weight

        with transaction.atomic():
            feed_ids = sorted({old_feed_id, new_feed.id})
            locked_feeds = {
                feed.id: feed
                for feed in FeedInfo.objects.select_for_update().filter(id__in=feed_ids)
            }

            if new_feed.id == old_feed_id:
                delta = new_feed_weight - old_feed_weight
                if delta > 0:
                    if locked_feeds[old_feed_id].stock_quantity < delta:
                        raise serializers.ValidationError({'feed_weight': '饲料库存不足'})
                    FeedInfo.objects.filter(pk=old_feed_id).update(stock_quantity=F('stock_quantity') - delta)
                elif delta < 0:
                    FeedInfo.objects.filter(pk=old_feed_id).update(stock_quantity=F('stock_quantity') + (-delta))
            else:
                FeedInfo.objects.filter(pk=old_feed_id).update(stock_quantity=F('stock_quantity') + old_feed_weight)
                if locked_feeds[new_feed.id].stock_quantity < new_feed_weight:
                    raise serializers.ValidationError({'feed_weight': '饲料库存不足'})
                FeedInfo.objects.filter(pk=new_feed.id).update(stock_quantity=F('stock_quantity') - new_feed_weight)

            return super().update(instance, validated_data)

class VaccinationRecordSerializer(serializers.ModelSerializer):
    """
    疫苗接种记录序列化器
    """
    batch_code = serializers.ReadOnlyField(source='batch.batch_code')
    farmer_name = serializers.ReadOnlyField(source='batch.farmer.farmer_name')

    class Meta:
        model = VaccinationRecord
        fields = '__all__'

class DiseaseReportSerializer(serializers.ModelSerializer):
    """
    疾病上报序列化器
    """
    batch_code = serializers.ReadOnlyField(source='batch.batch_code')
    farmer_name = serializers.ReadOnlyField(source='batch.farmer.farmer_name')
    handled_by_name = serializers.ReadOnlyField(source='handled_by.username')

    class Meta:
        model = DiseaseReport
        fields = '__all__'
        extra_kwargs = {
            'report_date': {'required': False, 'allow_null': True},
        }

    def validate(self, attrs):
        request = self.context.get('request')
        instance = getattr(self, 'instance', None)

        if instance is not None and 'batch' in attrs and attrs['batch'].id != instance.batch_id:
            raise serializers.ValidationError({'batch': '不允许修改关联批次'})

        affected_count = attrs.get('affected_count')
        if affected_count is not None and affected_count <= 0:
            raise serializers.ValidationError({'affected_count': '发病数量必须大于 0'})

        if request and request.user and request.user.is_authenticated and not request.user.is_staff:
            view = self.context.get('view')
            action_name = getattr(view, 'action', None)

            if action_name == 'audit' and instance is not None and request.user.groups.filter(name='vet').exists():
                if instance.handled_by_id != request.user.id:
                    raise serializers.ValidationError({'batch': '无权操作该批次'})
                return attrs

            batch = attrs.get('batch')
            if batch is None and instance is not None:
                batch = instance.batch
            
            if batch:
                if getattr(batch.farmer, 'user_id', None) != request.user.id:
                    raise serializers.ValidationError({'batch': '无权操作该批次'})

        return attrs

    def create(self, validated_data):
        batch = validated_data['batch']
        status = validated_data.get('status', 'pending')
        affected_count = validated_data.get('affected_count', 1)

        if not validated_data.get('report_date'):
            validated_data['report_date'] = timezone.now().date()

        with transaction.atomic():
            locked_batch = LivestockBatch.objects.select_for_update().get(pk=batch.pk)

            if status == 'died':
                if locked_batch.quantity < affected_count:
                    raise serializers.ValidationError({'affected_count': '死亡数量不能超过批次当前数量'})
                LivestockBatch.objects.filter(pk=locked_batch.pk).update(quantity=F('quantity') - affected_count)

            return DiseaseReport.objects.create(**validated_data)

    def update(self, instance, validated_data):
        if 'batch' in validated_data and validated_data['batch'].id != instance.batch_id:
            raise serializers.ValidationError({'batch': '不允许修改关联批次'})

        old_status = instance.status
        old_affected_count = instance.affected_count

        new_status = validated_data.get('status', old_status)
        new_affected_count = validated_data.get('affected_count', old_affected_count)

        old_died = old_status == 'died'
        new_died = new_status == 'died'

        with transaction.atomic():
            locked_batch = LivestockBatch.objects.select_for_update().get(pk=instance.batch_id)

            adjust = 0
            if not old_died and new_died:
                adjust = -new_affected_count
            elif old_died and not new_died:
                adjust = old_affected_count
            elif old_died and new_died:
                adjust = -(new_affected_count - old_affected_count)

            if adjust < 0:
                need = -adjust
                if locked_batch.quantity < need:
                    raise serializers.ValidationError({'affected_count': '死亡数量不能超过批次当前数量'})
                LivestockBatch.objects.filter(pk=locked_batch.pk).update(quantity=F('quantity') - need)
            elif adjust > 0:
                LivestockBatch.objects.filter(pk=locked_batch.pk).update(quantity=F('quantity') + adjust)

            return super().update(instance, validated_data)