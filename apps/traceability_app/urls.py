"""
溯源模块路由（挂载前缀 ``/api/traceability/``）
================================================

- ``public``：按 ``trace_code`` 公开查询溯源详情（无需登录）。
- ``admin``：管理员溯源记录列表与删除。
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PublicTraceViewSet, AdminTraceViewSet

router = DefaultRouter()
router.register(r'public', PublicTraceViewSet, basename='trace-public')
router.register(r'admin', AdminTraceViewSet, basename='trace-admin')

urlpatterns = [
    path('', include(router.urls)),
]
