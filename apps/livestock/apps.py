"""牲畜管理应用：大类、养殖区域、批次（批次号生成见 ``models.LivestockBatch``）。"""
from django.apps import AppConfig


class LivestockConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'  # type: ignore
    name = 'apps.livestock'
    verbose_name = '牲畜管理'
