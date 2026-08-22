"""溯源应用：出栏批次关联溯源码、二维码图片及公开查询 API。"""
from django.apps import AppConfig


class TraceabilityAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'  # type: ignore
    name = 'apps.traceability_app'
    verbose_name = '质量溯源管理'
