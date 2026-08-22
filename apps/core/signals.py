"""
Django 模型信号 — 数据变更后触发实时刷新
==========================================

在 ``apps.core.apps.CoreConfig.ready`` 中调用 ``connect_signals()``，为下列模型的
``post_save`` / ``post_delete`` 注册同一处理器：根据模型类名生成 ``data_type``（小写），
再调用 ``send_refresh_signal``，使各业务列表无需手写推送。

注意：
    - 下方 ``create_signal_handler`` 为历史遗留样板，当前实际使用的是模块级
      ``universal_refresh_handler``；保留前者仅为避免误删时的困惑。
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .utils import send_refresh_signal

# 参与「列表实时刷新」的模型（app_label.ModelName）
MODELS_TO_WATCH = [
    'livestock.LivestockArea',
    'livestock.LivestockBatch',
    'livestock.LivestockCategory',
    'production.FeedInfo',
    'production.FeedingRecord',
    'production.VaccinationRecord',
    'production.DiseaseReport',
]

def create_signal_handler(model_name):
    @receiver(post_save, sender=model_name)
    @receiver(post_delete, sender=model_name)
    def universal_refresh_handler(sender, instance, **kwargs):
        """
        当数据保存或删除时，触发实时刷新
        """
        # 获取模型小写名称作为 data_type，方便前端按需刷新
        data_type = sender.__name__.lower()
        send_refresh_signal(data_type=data_type)

def connect_signals():
    """应用启动后调用：把 ``MODELS_TO_WATCH`` 中每个模型绑定到 ``universal_refresh_handler``。"""
    from django.apps import apps
    for model_path in MODELS_TO_WATCH:
        try:
            model = apps.get_model(model_path)
            post_save.connect(universal_refresh_handler, sender=model)
            post_delete.connect(universal_refresh_handler, sender=model)
        except Exception as e:
            print(f"Error connecting signals for {model_path}: {e}")


def universal_refresh_handler(sender, instance, **kwargs):
    """
    任意监听模型保存或删除后调用：推送 ``sender.__name__.lower()`` 作为 ``data_type``。
    """
    data_type = sender.__name__.lower()
    send_refresh_signal(data_type=data_type)
