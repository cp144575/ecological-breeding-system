"""
文件功能：生产管理模块模型定义，包含饲料、喂养、疫苗及疾病记录
"""
from django.db import models
from django.utils import timezone
from django.conf import settings
from apps.users.models import FarmerProfile
from apps.livestock.models import LivestockBatch
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.db.models.manager import Manager

class FeedInfo(models.Model):
    """
    饲料信息表
    """
    if TYPE_CHECKING:
        objects: 'Manager'
    
    farmer = models.ForeignKey(FarmerProfile, on_delete=models.CASCADE, related_name='feeds', verbose_name="所属养殖户")
    feed_name = models.CharField(max_length=100, verbose_name="饲料名称")
    image = models.ImageField(upload_to='feeds/', null=True, blank=True, verbose_name="饲料图片")
    introduction = models.TextField(null=True, blank=True, verbose_name="饲料简介")
    unit = models.CharField(max_length=50, default='kg', editable=False, verbose_name="计量单位")
    stock_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="当前库存量")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="入库时间")

    class Meta:
        db_table = 'production_feed'
        verbose_name = '饲料信息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.feed_name

class FeedingRecord(models.Model):
    """
    喂养记录表
    """
    if TYPE_CHECKING:
        objects: 'Manager'
    
    batch = models.ForeignKey(LivestockBatch, on_delete=models.CASCADE, related_name='feeding_records', verbose_name="关联批次")
    feed = models.ForeignKey(FeedInfo, on_delete=models.PROTECT, verbose_name="关联饲料")
    feed_weight = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="投喂重量")
    feeding_time = models.DateTimeField(default=timezone.now, verbose_name="投喂时间")
    remark = models.TextField(null=True, blank=True, verbose_name="备注")

    class Meta:
        db_table = 'production_feeding'
        verbose_name = '喂养记录'
        verbose_name_plural = verbose_name

class VaccinationRecord(models.Model):
    """
    疫苗接种记录表
    """
    if TYPE_CHECKING:
        objects: 'Manager'
    
    batch = models.ForeignKey(LivestockBatch, on_delete=models.CASCADE, related_name='vaccinations', verbose_name="关联批次")
    vaccine_name = models.CharField(max_length=100, verbose_name="疫苗名称")
    vaccination_date = models.DateField(verbose_name="接种日期")
    next_vaccination_date = models.DateField(null=True, blank=True, verbose_name="下次接种日期")
    remark = models.TextField(null=True, blank=True, verbose_name="备注")

    class Meta:
        db_table = 'production_vaccine'
        verbose_name = '疫苗接种'
        verbose_name_plural = verbose_name

class DiseaseReport(models.Model):
    """
    疾病上报记录表
    """
    if TYPE_CHECKING:
        objects: 'Manager'
    
    STATUS_CHOICES = (
        ('pending', '待处理'),
        ('treating', '治疗中'),
        ('recovered', '已康复'),
        ('died', '死亡'),
    )
    batch = models.ForeignKey(LivestockBatch, on_delete=models.CASCADE, related_name='diseases', verbose_name="关联批次")
    disease_name = models.CharField(max_length=100, verbose_name="疾病名称")
    symptoms = models.TextField(verbose_name="症状描述")
    affected_count = models.IntegerField(default=1, verbose_name="发病数量")  # type: ignore
    report_date = models.DateField(db_index=True, verbose_name="上报日期")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="处理状态")
    treatment_plan = models.TextField(null=True, blank=True, verbose_name="处理意见")
    handled_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='handled_disease_reports', verbose_name="处理人")
    handled_at = models.DateTimeField(null=True, blank=True, verbose_name="处理时间")

    class Meta:
        db_table = 'production_disease'
        verbose_name = '疾病上报'
        verbose_name_plural = verbose_name