"""生产防疫应用：饲料库存、投喂、疫苗接种、疾病上报。"""
from django.apps import AppConfig


class ProductionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'  # type: ignore
    name = 'apps.production'
    verbose_name = '生产防疫'
