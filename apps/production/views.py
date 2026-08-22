"""
生产防疫 REST 接口
==================

- ``FeedInfoViewSet``：饲料档案与库存（养殖户）。
- ``FeedingRecordViewSet``：投喂记录；删除时回冲库存。
- ``VaccinationRecordViewSet``：疫苗记录。
- ``DiseaseReportViewSet``：疾病上报；含管理员 ``assign``、兽医 ``audit``、死亡数量与批次联动。

权限在 ``get_permissions`` / ``get_queryset`` 中按管理员 / 兽医 / 养殖户细分。
"""
from django.db import transaction
from django.db.models import F
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from apps.core.utils import BaseOwnerViewSet, send_refresh_signal
from .models import FeedInfo, FeedingRecord, VaccinationRecord, DiseaseReport
from .serializers import (
    FeedInfoSerializer, FeedingRecordSerializer, 
    VaccinationRecordSerializer, DiseaseReportSerializer
)
from apps.livestock.models import LivestockBatch
from apps.users.permissions import IsAdminUser, IsVerifiedFarmer, IsVetUser

User = get_user_model()

class FeedInfoViewSet(BaseOwnerViewSet):
    """
    饲料信息视图集
    """
    queryset = FeedInfo.objects.all()
    serializer_class = FeedInfoSerializer
    search_fields = ['feed_name']
    select_related_fields = ['farmer']

class DiseaseReportViewSet(BaseOwnerViewSet):
    """
    疾病上报视图集
    """
    queryset = DiseaseReport.objects.all()
    serializer_class = DiseaseReportSerializer
    search_fields = ['disease_name', 'symptoms', 'batch__batch_code']
    owner_field = 'batch__farmer'
    filterset_fields = ['batch', 'status']

    def get_queryset(self):
        queryset = DiseaseReport.objects.all().order_by('-id')
        user = self.request.user

        if user.is_staff:
            return queryset

        if user.groups.filter(name='vet').exists():
            return queryset.filter(handled_by=user)

        return queryset.filter(batch__farmer__user=user)

    def get_permissions(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return super().get_permissions()

        if self.action == 'create':
            return [IsVerifiedFarmer()]

        if self.action == 'audit':
            return [IsVetUser()]

        if self.action == 'assign':
            return [IsAdminUser()]

        return super().get_permissions()

    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        """
        管理员将疾病上报指派给兽医
        """
        report = self.get_object()
        vet_user_id = request.data.get('vet_user_id')
        if not vet_user_id:
            return Response({'error': '缺少兽医用户标识'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            vet_user = User.objects.get(pk=vet_user_id)
        except User.DoesNotExist:
            return Response({'error': '兽医用户不存在'}, status=status.HTTP_400_BAD_REQUEST)

        if vet_user.is_staff or (not vet_user.groups.filter(name='vet').exists()):
            return Response({'error': '该用户不是兽医'}, status=status.HTTP_400_BAD_REQUEST)

        report.handled_by = vet_user
        report.handled_at = None
        report.save(update_fields=['handled_by', 'handled_at'])

        send_refresh_signal(data_type="diseasereport")
        return Response({'message': '分配成功'})

    @action(detail=True, methods=['post'])
    def audit(self, request, pk=None):
        report = self.get_object()
        new_status = request.data.get('status')
        treatment_plan = request.data.get('treatment_plan')
        
        valid_statuses = [choice[0] for choice in DiseaseReport.STATUS_CHOICES]
        if new_status not in valid_statuses:
            return Response({'error': '无效的状态'}, status=status.HTTP_400_BAD_REQUEST)

        if report.handled_by_id and report.handled_by_id != request.user.id:
            return Response({'error': '无权处理该记录'}, status=status.HTTP_403_FORBIDDEN)

        with transaction.atomic():
            locked_report = DiseaseReport.objects.select_for_update().get(pk=report.pk)

            if locked_report.status != 'died' and new_status == 'died':
                locked_batch = LivestockBatch.objects.select_for_update().get(pk=locked_report.batch_id)
                if locked_batch.quantity < locked_report.affected_count:
                    return Response({'error': '死亡数量不能超过批次当前数量'}, status=status.HTTP_400_BAD_REQUEST)
                LivestockBatch.objects.filter(pk=locked_batch.pk).update(
                    quantity=F('quantity') - locked_report.affected_count
                )

            if locked_report.status == 'died' and new_status != 'died':
                LivestockBatch.objects.select_for_update().filter(pk=locked_report.batch_id).update(
                    quantity=F('quantity') + locked_report.affected_count
                )

            updated_data = {
                'status': new_status,
                'handled_by': request.user.id,
                'handled_at': timezone.now(),
            }

            if treatment_plan is not None:
                updated_data['treatment_plan'] = treatment_plan

            serializer = self.get_serializer(locked_report, data=updated_data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()

        send_refresh_signal(data_type="diseasereport")

        return Response({'message': '处理成功'})

    def perform_destroy(self, instance):
        user = self.request.user
        if not user.is_staff:
            owner = instance
            for part in self.owner_field.split('__'):
                owner = getattr(owner, part)
            if owner.user != user:
                raise PermissionDenied("您无权删除此数据")

        with transaction.atomic():
            if instance.status == 'died':
                LivestockBatch.objects.select_for_update().filter(pk=instance.batch_id).update(
                    quantity=F('quantity') + instance.affected_count
                )
            instance.delete()

        send_refresh_signal(data_type=instance.__class__.__name__.lower())

class FeedingRecordViewSet(BaseOwnerViewSet):
    """
    喂养记录视图集
    """
    queryset = FeedingRecord.objects.all()
    serializer_class = FeedingRecordSerializer
    search_fields = ['batch__batch_code', 'feed__feed_name']
    owner_field = 'batch__farmer'
    filterset_fields = ['batch']
    select_related_fields = ['batch', 'batch__farmer', 'feed']

    def perform_destroy(self, instance):
        user = self.request.user
        if not user.is_staff:
            owner = instance
            for part in self.owner_field.split('__'):
                owner = getattr(owner, part)
            if owner.user != user:
                raise PermissionDenied("您无权删除此数据")

        with transaction.atomic():
            FeedInfo.objects.select_for_update().filter(pk=instance.feed_id).update(
                stock_quantity=F('stock_quantity') + instance.feed_weight
            )
            instance.delete()

        send_refresh_signal(data_type=instance.__class__.__name__.lower())

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsVerifiedFarmer()]
        return super().get_permissions()

class VaccinationRecordViewSet(BaseOwnerViewSet):
    """
    疫苗接种记录视图集
    """
    queryset = VaccinationRecord.objects.all()
    serializer_class = VaccinationRecordSerializer
    search_fields = ['batch__batch_code', 'vaccine_name', 'remark']
    owner_field = 'batch__farmer'
    filterset_fields = ['batch']
    select_related_fields = ['batch', 'batch__farmer']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsVerifiedFarmer()]
        return super().get_permissions()