"""
数据统计模块路由 — 前缀 ``/api/stats/``
======================================
"""
from django.urls import path
from .views import AdminDashboardStatsView, FarmerDashboardStatsView

urlpatterns = [
    path('admin/dashboard/', AdminDashboardStatsView.as_view(), name='admin-stats'),
    path('farmer/dashboard/', FarmerDashboardStatsView.as_view(), name='farmer-stats'),
]
