"""用户与认证应用（自定义 User、养殖户/管理员扩展、资质认证）。"""
from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'  # type: ignore
    name = 'apps.users'
    verbose_name = '用户与认证'
