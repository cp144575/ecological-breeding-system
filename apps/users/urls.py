"""
用户模块 URL 路由
================

前缀由根 ``urls.py`` 挂载为 ``/api/users/``：
登录、刷新令牌、注册，以及 ``profile`` / ``cert`` / ``farmer`` 三个 DefaultRouter 资源集。
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import RegisterView, UserProfileViewSet, CertificationViewSet, FarmerViewSet, CustomTokenObtainPairView

router = DefaultRouter()
router.register(r'profile', UserProfileViewSet, basename='user-profile')
router.register(r'cert', CertificationViewSet, basename='certification')
router.register(r'farmer', FarmerViewSet, basename='farmer')

urlpatterns = [
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', RegisterView.as_view(), name='register'),
    path('', include(router.urls)),
]
