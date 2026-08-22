"""
生产防疫模块路由 — 前缀 ``/api/production/``
===========================================
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    FeedInfoViewSet, FeedingRecordViewSet, 
    VaccinationRecordViewSet, DiseaseReportViewSet
)

router = DefaultRouter()
router.register(r'feed', FeedInfoViewSet)
router.register(r'feeding', FeedingRecordViewSet)
router.register(r'vaccination', VaccinationRecordViewSet)
router.register(r'disease', DiseaseReportViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
