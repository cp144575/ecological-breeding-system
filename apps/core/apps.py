"""
apps.core — 公共基础设施应用
============================

包含：分页、WebSocket 路由与消费者、全局信号刷新、DRF 视图基类工具（``utils``）、
抽象模型 ``StatusMixin``（审核流）等。无独立业务表或极少。
"""
from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'  # type: ignore
    name = 'apps.core'
    verbose_name = '核心公共'

    def ready(self):
        """Django 启动完成后连接 ``signals.connect_signals``，启用模型变更广播。"""
        from . import signals
        signals.connect_signals()
