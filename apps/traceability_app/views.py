"""
溯源 REST 接口
==============

- ``PublicTraceViewSet``：公开只读，lookup 为 ``trace_code``，权限 ``AllowAny``。
- ``AdminTraceViewSet``：管理员列表/删除；删除后推送刷新信号。
"""
from rest_framework import mixins, viewsets, permissions
from .models import LivestockTrace
from .serializers import PublicTraceDetailSerializer, AdminTraceSerializer
from apps.core.utils import send_refresh_signal

class PublicTraceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    公开溯源查询接口 - 无需登录即可访问
    """
    queryset = LivestockTrace.objects.filter(is_active=True)
    serializer_class = PublicTraceDetailSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'trace_code'

class AdminTraceViewSet(
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """
    后台溯源管理接口 - 仅限管理员
    """
    queryset = LivestockTrace.objects.all().order_by('-id')
    serializer_class = AdminTraceSerializer
    permission_classes = [permissions.IsAdminUser]
    filterset_fields = ['batch__farmer', 'is_active']
    search_fields = ['trace_code', 'batch__batch_code']

    def perform_destroy(self, instance):
        instance.delete()
        send_refresh_signal(data_type="trace")