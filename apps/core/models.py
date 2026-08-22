"""
抽象模型 — 审核流字段复用
==========================

凡需「待审核 / 通过 / 驳回」流程的业务模型可继承 ``StatusMixin``，
避免在每张表重复定义 ``status``、``audit_remark``、``audit_time``。
"""
from django.db import models


class StatusMixin(models.Model):
    """
    通用审核状态抽象模型（``abstract = True``，不产生独立数据表）。
    """
    STATUS_CHOICES = (
        (0, '待审核'),
        (1, '审核通过'),
        (2, '审核驳回'),
    )
    status = models.IntegerField(choices=STATUS_CHOICES, default=0, verbose_name="审核状态")  # type: ignore
    audit_remark = models.TextField(null=True, blank=True, verbose_name="审核备注")
    audit_time = models.DateTimeField(null=True, blank=True, verbose_name="审核时间")
    
    class Meta:
        abstract = True
