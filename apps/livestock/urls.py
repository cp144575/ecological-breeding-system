"""
牲畜模块路由 — 前缀 ``/api/livestock/``
======================================
注册 ``category`` / ``area`` / ``batch`` 三个 ViewSet。
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    LivestockCategoryViewSet, LivestockAreaViewSet, 
    LivestockBatchViewSet
)

router = DefaultRouter()
router.register(r'category', LivestockCategoryViewSet)
router.register(r'area', LivestockAreaViewSet)
router.register(r'batch', LivestockBatchViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
