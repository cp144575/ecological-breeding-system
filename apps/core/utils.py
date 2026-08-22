"""
apps.core.utils — 核心公共工具与视图基类
==========================================

主要内容包括：
    - ``BasePublicViewSet`` / ``BaseOwnerViewSet``：列表读写权限与所有权校验、写操作后 WebSocket 广播。
    - ``send_refresh_signal``：向 Channels 组 ``data_refresh_group`` 推送 JSON 文本，驱动前端列表刷新。
    - ``encrypt_id_card`` / ``decrypt_id_card`` / ``mask_id_card``：证件号存储加密与展示脱敏。
    - ``get_image_upload_error``：上传图片文件名、大小、扩展名、Content-Type 校验。

依赖 ``channels.layers`` 与 ``asgiref.sync.async_to_sync``；若无 Channel Layer（极少见），推送为空操作。
"""
import base64
import json
import os
import re
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from rest_framework import viewsets, filters, permissions
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import PermissionDenied
from apps.users.permissions import IsVerifiedFarmer, IsAdminUser

class DenyAll(permissions.BasePermission):
    """
    权限恒为 False；用于 ``BaseOwnerViewSet`` 中禁止管理员提交养殖户业务数据（配合 ``get_permissions``）。
    """
    def has_permission(self, _request, _view):
        return False

class BasePublicViewSet(viewsets.ModelViewSet):
    """
    基础公共视图集：
    1. 所有人（登录用户）可读。
    2. 仅管理员可写（增删改）。
    3. 自动发送 WebSocket 刷新信号。
    """
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    ordering_fields = '__all__'

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'search']:
            return [permissions.IsAuthenticated()]
        return [IsAdminUser()]

    def perform_create(self, serializer):
        instance = serializer.save()
        send_refresh_signal(data_type=instance.__class__.__name__.lower())

    def perform_update(self, serializer):
        instance = serializer.save()
        send_refresh_signal(data_type=instance.__class__.__name__.lower())

    def perform_destroy(self, instance):
        data_type = instance.__class__.__name__.lower()
        instance.delete()
        send_refresh_signal(data_type=data_type)

class BaseOwnerViewSet(viewsets.ModelViewSet):
    """
    基础所有权视图集：
    1. 管理员查看全部数据，养殖户仅查看自身数据。
    2. 自动处理 perform_create 以关联当前养殖户。
    3. 自动校验写操作权限（必须通过认证）。
    """
    owner_field = 'farmer'  # 模型中关联养殖户的字段名
    user_owner_path = 'farmer_profile' # 用户模型关联养殖户 Profile 的路径
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    ordering_fields = '__all__'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        
        # 处理 select_related 优化
        if hasattr(self, 'select_related_fields'):
            queryset = queryset.select_related(*self.select_related_fields)
            
        if user.is_staff:
            return queryset.order_by('-id')
            
        # 根据 owner_field 过滤
        # 如果是直接关联到 FarmerProfile
        if self.owner_field == 'farmer':
            filter_kwargs = {'farmer__user': user}
        # 如果是关联到 batch (batch 关联到 farmer)
        elif self.owner_field == 'batch__farmer':
            filter_kwargs = {'batch__farmer__user': user}
        # 如果是关联到 farmer (farmer 关联到 user)
        elif self.owner_field == 'farmer_profile':
            filter_kwargs = {'user': user}
        else:
            # 通用兜底
            filter_kwargs = {f"{self.owner_field}__user": user}
            
        return queryset.filter(**filter_kwargs).order_by('-id')

    def get_permissions(self):
        """
        权限精细化控制：
        1. 养殖户：写操作需通过认证
        2. 管理员：禁止增、改（除非子类另行规定）
        """
        user = self.request.user
        if not user.is_authenticated:
            return super().get_permissions()

        # 养殖户写操作必须认证
        if not user.is_staff and self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsVerifiedFarmer()]
            
        # 管理员默认禁止创建和修改业务数据
        if user.is_staff and self.action in ['create', 'update', 'partial_update']:
            return [DenyAll()]
            
        return super().get_permissions()

    def perform_create(self, serializer):
        """
        创建时自动关联养殖户
        """
        if self.request.user.is_staff:
            raise PermissionDenied("管理员无法创建此项数据")
        
        # 自动填充 owner_field
        save_kwargs = {}
        if self.owner_field and '__' not in self.owner_field:
            save_kwargs[self.owner_field] = getattr(self.request.user, self.user_owner_path)
            
        instance = serializer.save(**save_kwargs)
        # 发送刷新信号
        send_refresh_signal(data_type=instance.__class__.__name__.lower())

    def perform_update(self, serializer):
        """
        更新时检查所有权
        """
        instance = self.get_object()
        if not self.request.user.is_staff:
            owner = instance
            for part in self.owner_field.split('__'):
                owner = getattr(owner, part)
            
            if owner.user != self.request.user:
                raise PermissionDenied("您无权修改此数据")
        
        updated_instance = serializer.save()
        # 发送刷新信号
        send_refresh_signal(data_type=updated_instance.__class__.__name__.lower())

    def perform_destroy(self, instance):
        """
        删除时检查所有权
        """
        data_type = instance.__class__.__name__.lower()
        if not self.request.user.is_staff:
            owner = instance
            for part in self.owner_field.split('__'):
                owner = getattr(owner, part)
                
            if owner.user != self.request.user:
                raise PermissionDenied("您无权删除此数据")
        instance.delete()
        # 发送刷新信号
        send_refresh_signal(data_type=data_type)

def send_refresh_signal(data_type: str = "all", message: str = "Data updated"):
    """
    发送 WebSocket 刷新信号给所有客户端。
    负载只序列化一次，减少消费者侧 CPU；async_to_sync 与当前项目 asgiref 版本兼容（不传 thread_sensitive）。
    """
    channel_layer = get_channel_layer()
    if channel_layer:
        text_data = json.dumps(
            {"type": "refresh", "data_type": data_type, "message": message},
            separators=(",", ":"),
        )
        async_to_sync(channel_layer.group_send)(
            "data_refresh_group",
            {
                "type": "refresh_message",
                "text_data": text_data,
            },
        )

def encrypt_id_card(id_card: str) -> str:
    """
    简易加密身份证号 (Base64 + 偏移，实际生产应使用 AES 等)
    """
    if not id_card:
        return ""
    # 模拟加密逻辑
    encoded = base64.b64encode(id_card.encode()).decode()
    return f"ENC_{encoded}"

def decrypt_id_card(encrypted_id_card: str) -> str:
    """
    简易解密身份证号
    """
    if not encrypted_id_card or not encrypted_id_card.startswith("ENC_"):
        return encrypted_id_card
    try:
        encoded = encrypted_id_card[4:]
        return base64.b64decode(encoded).decode()
    except Exception:
        return encrypted_id_card


def mask_id_card(plain: str) -> str:
    """
    身份证号脱敏展示（不含加密，仅用于界面/API 输出）。
    - 18 位（末位可为数字或 X）：前 6 + 8 个 * + 后 4
    - 15 位一代证：前 6 + 5 个 * + 后 4
    - 其它长度：首尾少量保留，中间 *；过短则尽量不打捞完整信息
    """
    if not plain:
        return ""
    s = str(plain).strip()
    if not s:
        return ""
    n = len(s)
    # 18 位中国大陆二代证（末位可为 X/x）
    if n == 18 and s[:17].isdigit() and (s[17].isdigit() or s[17].upper() == "X"):
        return f"{s[:6]}********{s[-4:]}"
    # 15 位一代身份证
    if n == 15 and s.isdigit():
        return f"{s[:6]}*****{s[-4:]}"
    if n <= 3:
        return "*" * n
    if n <= 6:
        return f"{s[0]}***{s[-1]}"
    return f"{s[:2]}{'*' * (n - 4)}{s[-2:]}"


def get_image_upload_error(uploaded_file):
    """
    校验上传图片是否符合业务约束。

    返回：
        None — 通过校验；
        str — 中文错误提示（文件名非法字符、超过 5MB、扩展名或 MIME 不在白名单）。
    """
    if not uploaded_file:
        return None

    filename = os.path.basename(getattr(uploaded_file, 'name', '') or '')
    if filename and not re.match(r'^[\u4e00-\u9fa5a-zA-Z0-9_.-]+$', filename):
        return '文件名不允许包含特殊字符'

    if getattr(uploaded_file, 'size', 0) and uploaded_file.size > 5 * 1024 * 1024:
        return '图片大小不能超过5MB'

    ext = os.path.splitext(filename)[1].lower() if filename else ''
    if ext and ext not in {'.jpg', '.jpeg', '.png', '.gif'}:
        return '请上传JPG/PNG/GIF格式图片'

    content_type = (getattr(uploaded_file, 'content_type', '') or '').lower()
    if content_type and content_type not in {'image/jpeg', 'image/png', 'image/gif'}:
        return '请上传JPG/PNG/GIF格式图片'

    return None