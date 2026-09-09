"""
用户模块 HTTP 接口
==================

视图说明：
    - ``CustomTokenObtainPairView``：JWT 登录（路径 ``/api/users/login/``）。
    - ``RegisterView``：开放注册。
    - ``UserProfileViewSet``：用户列表（管理员）、当前用户 ``info``、改资料、头像上传、改密、禁用账号。
    - ``CertificationViewSet``：养殖户资质 CRUD、``my_cert``、管理员 ``audit``。
    - ``FarmerViewSet``：管理员查看养殖户档案列表。

头像上传使用 Pillow 生成缩略图后写入 ``User.avatar``。
"""
from rest_framework import viewsets, status, generics, filters, mixins
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from .models import FarmerProfile, Certification
from .serializers import (
    UserDetailSerializer, RegisterSerializer, FarmerProfileSerializer,
    CertificationSerializer, CustomTokenObtainPairSerializer
)
from apps.core.utils import BaseOwnerViewSet, send_refresh_signal
from .permissions import IsAdminUser, IsFarmerUser
from django.utils import timezone
from PIL import Image
import warnings
import io
from django.core.files.base import ContentFile
import os
import re
import logging

logger = logging.getLogger(__name__)

User = get_user_model()

class CustomTokenObtainPairView(TokenObtainPairView):
    """
    自定义登录视图，使用带角色校验的序列化器
    """
    serializer_class = CustomTokenObtainPairSerializer

class RegisterView(generics.CreateAPIView):
    """
    用户注册视图
    """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

class UserProfileViewSet(mixins.ListModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    """
    用户个人信息视图集
    """
    queryset = User.objects.all()
    serializer_class = UserDetailSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['username', 'phone']

    def get_queryset(self):
        """
        管理员可以查看所有用户，普通用户只能查看自己
        """
        user = self.request.user
        if user.is_staff:
            return User.objects.all().order_by('-date_joined')
        return User.objects.filter(id=user.id)

    def perform_update(self, serializer):
        serializer.save()
        send_refresh_signal(data_type="user")

    def perform_destroy(self, instance):
        instance.delete()
        send_refresh_signal(data_type="user")

    @action(detail=False, methods=['get'])
    def info(self, request):
        """
        获取当前登录用户信息
        """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['patch'])
    def update_info(self, request):
        """
        更新个人基本信息
        """
        user = request.user
        if 'phone' not in request.data:
            return Response({'error': '缺少手机号字段'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(user, data={'phone': request.data.get('phone')}, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        send_refresh_signal(data_type="user")
        return Response({'message': '基本信息更新成功'})

    @action(detail=False, methods=['post'])
    def upload_avatar(self, request):
        """
        上传头像并生成缩略图
        """
        user = request.user
        avatar_file = request.FILES.get('avatar')

        if not avatar_file:
            return Response({'error': '未选择图片文件'}, status=status.HTTP_400_BAD_REQUEST)

        filename = os.path.basename(avatar_file.name)
        if not re.match(r'^[\u4e00-\u9fa5a-zA-Z0-9_.-]+$', filename):
            return Response({'error': '文件名不允许包含特殊字符'}, status=status.HTTP_400_BAD_REQUEST)

        # 验证文件大小 (5MB)
        if avatar_file.size > 5 * 1024 * 1024:
            return Response({'error': '图片大小不能超过5MB'}, status=status.HTTP_400_BAD_REQUEST)

        # 验证文件类型
        ext = os.path.splitext(avatar_file.name)[1].lower()
        if ext not in ['.jpg', '.jpeg', '.png', '.gif']:
            return Response({'error': '请上传JPG/PNG/GIF格式图片'}, status=status.HTTP_400_BAD_REQUEST)

        max_image_pixels_backup = Image.MAX_IMAGE_PIXELS
        try:
            Image.MAX_IMAGE_PIXELS = None

            avatar_file.seek(0)
            with warnings.catch_warnings():
                warnings.simplefilter('ignore', Image.DecompressionBombWarning)
                img = Image.open(avatar_file)
                try:
                    img.draft('RGB', (200, 200))
                except Exception:
                    pass

                if img.mode != 'RGB':
                    img = img.convert('RGB')

                img.thumbnail((200, 200), Image.Resampling.LANCZOS)

                thumb_io = io.BytesIO()
                img.save(thumb_io, format='JPEG', quality=85)
                thumb_file = ContentFile(thumb_io.getvalue(), name=f"{user.username}_avatar.jpg")

                user.avatar.save(thumb_file.name, thumb_file, save=True)
                send_refresh_signal(data_type="user")

                return Response({
                    'message': '头像上传成功',
                    'avatar_url': user.avatar.url
                })
        except getattr(Image, 'DecompressionBombError', Exception):
            return Response({'error': '图片处理失败'}, status=status.HTTP_400_BAD_REQUEST)
        except MemoryError:
            return Response({'error': '图片过大，处理失败'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            # 详细异常仅写入服务端日志，避免将内部实现信息返回给客户端。
            logger.exception("Avatar upload processing failed (details kept server-side)")
            return Response({'error': '图片处理失败'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        finally:
            Image.MAX_IMAGE_PIXELS = max_image_pixels_backup

    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """
        修改密码
        """
        user = request.user
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')

        if not user.check_password(old_password):
            return Response({'error': '旧密码错误'}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        send_refresh_signal(data_type="user")
        return Response({'message': '密码修改成功'})

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def toggle_active(self, request, pk=None):
        """
        启用/禁用用户 (仅限管理员)
        """
        user = self.get_object()
        if user == request.user:
            return Response({'error': '不能禁用自己'}, status=status.HTTP_400_BAD_REQUEST)

        user.is_active = not user.is_active
        user.save()

        send_refresh_signal(data_type="user")

        status_str = "启用" if user.is_active else "禁用"
        return Response({'message': f'用户已{status_str}'})

class CertificationViewSet(BaseOwnerViewSet):
    """
    认证申请视图集
    """
    queryset = Certification.objects.all()
    serializer_class = CertificationSerializer
    filterset_fields = ['status']
    search_fields = ['farmer__farmer_name']

    def get_permissions(self):
        """
        覆盖基础权限：认证申请不需要先通过认证
        """
        if self.action == 'create':
            return [IsAuthenticated(), IsFarmerUser()]
        return super().get_permissions()

    @action(detail=False, methods=['get'])
    def my_cert(self, request):
        """
        获取当前养殖户的最新的认证信息
        """
        user = request.user
        if not hasattr(user, 'farmer_profile'):
            return Response({'error': '当前用户不是养殖户'}, status=status.HTTP_400_BAD_REQUEST)

        cert = Certification.objects.filter(farmer=user.farmer_profile).order_by('-created_at').first()
        if not cert:
            return Response(None, status=status.HTTP_200_OK)

        serializer = self.get_serializer(cert)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def audit(self, request, pk=None):
        """
        审核认证申请
        """
        instance = self.get_object()
        status_val = request.data.get('status') # 1: 通过, 2: 驳回
        remark = request.data.get('remark') or request.data.get('audit_remark', '')

        if status_val not in [1, 2]:
            return Response({'error': '无效的状态值'}, status=status.HTTP_400_BAD_REQUEST)

        instance.status = status_val
        instance.audit_remark = remark
        instance.audit_time = timezone.now()
        instance.save()

        # 如果审核通过，同步更新养殖户 Profile 的认证状态
        if status_val == 1:
            send_refresh_signal(data_type="user") # 同时刷新用户信息以更新认证图标

            farmer = instance.farmer
            farmer.is_verified = True
            # 如果认证中提供了身份证号，同步到个人 Profile
            if instance.id_card:
                farmer.id_card = instance.id_card
            farmer.save()

        send_refresh_signal(data_type="certification")

        return Response({'message': '审核操作成功'})

class FarmerViewSet(viewsets.ReadOnlyModelViewSet):
    """
    养殖户列表视图集 (仅限管理员查看)
    """
    queryset = FarmerProfile.objects.all()
    serializer_class = FarmerProfileSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['farmer_name', 'id_card', 'address']
