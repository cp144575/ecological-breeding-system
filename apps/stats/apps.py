"""数据统计应用：仅 ``views`` 提供仪表盘聚合接口；无独立 models（查询跨其它应用表）。"""
from django.apps import AppConfig


class StatsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'  # type: ignore
    name = 'apps.stats'
    verbose_name = '数据统计'
