"""
溯源序列化器：公开查询聚合批次/区域/防疫投喂等疾病摘要；管理员列表展示溯源码与二维码 URL。
"""
from rest_framework import serializers
from apps.livestock.models import LivestockBatch, LivestockArea
from apps.production.models import VaccinationRecord, FeedingRecord, DiseaseReport
from .models import LivestockTrace


class RelativeImageField(serializers.ImageField):
    """``ImageField`` 输出为相对/绝对 URL 字符串，便于前端直接作 img src。"""

    def to_representation(self, value):
        if not value:
            return None
        try:
            return value.url
        except Exception:
            return None


class PublicBatchSerializer(serializers.ModelSerializer):
    image = RelativeImageField(read_only=True)

    class Meta:
        model = LivestockBatch
        fields = ['breed', 'entry_date', 'finish_date', 'image', 'introduction']

class PublicVaccinationSerializer(serializers.ModelSerializer):
    class Meta:
        model = VaccinationRecord
        fields = ['vaccine_name', 'vaccination_date']

class PublicDiseaseSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    class Meta:
        model = DiseaseReport
        fields = ['disease_name', 'report_date', 'status_display']

class PublicFeedingSerializer(serializers.ModelSerializer):
    feed_name = serializers.ReadOnlyField(source='feed.feed_name')
    class Meta:
        model = FeedingRecord
        fields = ['feed_name', 'feeding_time', 'feed_weight']

class PublicAreaSerializer(serializers.ModelSerializer):
    image = RelativeImageField(read_only=True)

    class Meta:
        model = LivestockArea
        fields = ['area_name', 'description', 'image']

class PublicTraceDetailSerializer(serializers.ModelSerializer):
    """
    面向公众展示的溯源详情序列化器
    """
    batch_info = PublicBatchSerializer(source='batch', read_only=True)
    vaccination_history = serializers.SerializerMethodField()
    feeding_history = serializers.SerializerMethodField()
    disease_history = serializers.SerializerMethodField()
    area_info = PublicAreaSerializer(source='batch.area', read_only=True)
    farmer_name = serializers.ReadOnlyField(source='batch.farmer.farmer_name')
    is_farmer_certified = serializers.SerializerMethodField()
    trace_url = serializers.SerializerMethodField()

    class Meta:
        model = LivestockTrace
        fields = [
            'trace_code', 'trace_url', 'created_at',
            'batch_info', 'vaccination_history', 'feeding_history', 
            'disease_history', 'area_info', 'farmer_name', 'is_farmer_certified'
        ]

    def get_trace_url(self, obj):
        """
        功能：返回公开溯源查询地址。

        参数：
            obj：当前溯源记录对象

        返回值：
            str：公开溯源查询地址
        """
        return obj.get_public_trace_url()

    def get_vaccination_history(self, obj):
        records = VaccinationRecord.objects.filter(batch=obj.batch).order_by('-vaccination_date')[:10]
        return PublicVaccinationSerializer(records, many=True).data

    def get_feeding_history(self, obj):
        records = FeedingRecord.objects.filter(batch=obj.batch).order_by('-feeding_time')[:10]
        return PublicFeedingSerializer(records, many=True).data
    
    def get_disease_history(self, obj):
        records = DiseaseReport.objects.filter(batch=obj.batch).order_by('-report_date')[:10]
        return PublicDiseaseSerializer(records, many=True).data

    def get_is_farmer_certified(self, obj):
        return obj.batch.farmer.is_certified

class AdminTraceSerializer(serializers.ModelSerializer):
    """
    管理员溯源管理序列化器
    """
    batch_code = serializers.ReadOnlyField(source='batch.batch_code')
    farmer_name = serializers.ReadOnlyField(source='batch.farmer.farmer_name')
    qr_code_image = RelativeImageField(read_only=True)
    trace_url = serializers.SerializerMethodField()

    class Meta:
        model = LivestockTrace
        fields = (
            'id',
            'batch',
            'batch_code',
            'farmer_name',
            'trace_code',
            'trace_url',
            'qr_code_image',
            'is_active',
            'created_at',
        )
        read_only_fields = (
            'id',
            'batch_code',
            'farmer_name',
            'trace_code',
            'trace_url',
            'is_active',
            'created_at',
        )

    def get_trace_url(self, obj):
        """
        功能：返回管理员侧展示使用的公开溯源查询地址。

        参数：
            obj：当前溯源记录对象

        返回值：
            str：公开溯源查询地址
        """
        return obj.get_public_trace_url()