"""
用户模块序列化器
================

职责概览：
    - JWT 登录 ``CustomTokenObtainPairSerializer``：校验账号状态并在载荷中附带 ``role``。
    - ``UserDetailSerializer`` / ``FarmerProfileSerializer``：个人资料；证件号仅脱敏输出。
    - ``CertificationSerializer``：资质认证读写；``id_card_full`` 仅管理员可取明文。
    - ``RegisterSerializer``：注册仅用户名+密码，并自动创建 ``FarmerProfile``。
"""
from rest_framework import serializers, exceptions
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from apps.core.utils import get_image_upload_error
from .models import AdminProfile, FarmerProfile, Certification

User = get_user_model()

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    自定义 JWT 登录序列化器，不再依赖前端传参校验角色
    """
    def validate(self, attrs):
        # 预先检查用户是否存在且被禁用
        username = attrs.get(self.username_field)
        if username:
            try:
                user = User.objects.get(**{self.username_field: username})
                if not user.is_active:
                    # 使用 AuthenticationFailed 确保返回 401 状态码
                    raise exceptions.AuthenticationFailed('该账号已被禁用，请联系管理员')
            except User.DoesNotExist:
                pass 

        # 调用父类验证方法
        try:
            data = super().validate(attrs)
        except exceptions.AuthenticationFailed as e:
            # 如果是默认的“无活跃账号”错误，且我们前面没捕获到（说明是密码错误）
            # 则统一提示账号或密码错误
            raise e
        except Exception as e:
            raise e

        user = getattr(self, 'user', None)
        if user is None:
            raise exceptions.AuthenticationFailed('账号或密码错误')
        
        # 系统自动识别用户角色并包含在响应中
        if user.is_staff:
            data['role'] = 'admin'
        elif user.groups.filter(name='vet').exists():
            data['role'] = 'vet'
        else:
            data['role'] = 'farmer'
        data['username'] = user.username
        
        return data

class CertificationSerializer(serializers.ModelSerializer):
    """
    资格认证序列化器
    """
    farmer_name = serializers.ReadOnlyField(source='farmer.farmer_name')
    id_card = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    id_card_full = serializers.SerializerMethodField()

    class Meta:
        model = Certification
        fields = '__all__'
        read_only_fields = (
            'farmer',
            'status',
            'audit_remark',
            'audit_time',
            'created_at',
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # 列表/详情中 id_card 一律脱敏，避免前端误展示明文或写入日志
        data['id_card'] = instance.masked_id_card
        return data

    def get_id_card_full(self, obj):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        # 仅管理员审核时可取完整号码；养殖户与其它角色不提供明文通道
        if user and user.is_authenticated and user.is_staff:
            return obj.decrypted_id_card
        return None

    def validate_id_card_front(self, value):
        error_msg = get_image_upload_error(value)
        if error_msg:
            raise serializers.ValidationError(error_msg)
        return value

    def validate_id_card_back(self, value):
        error_msg = get_image_upload_error(value)
        if error_msg:
            raise serializers.ValidationError(error_msg)
        return value

    def validate_breeding_license(self, value):
        error_msg = get_image_upload_error(value)
        if error_msg:
            raise serializers.ValidationError(error_msg)
        return value

class UserSerializer(serializers.ModelSerializer):
    """
    基础用户序列化器
    """
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'role', 'phone', 'email', 'avatar')

    def get_role(self, obj):
        if obj.is_staff:
            return 'admin'
        if obj.groups.filter(name='vet').exists():
            return 'vet'
        return 'farmer'

class FarmerProfileSerializer(serializers.ModelSerializer):
    """
    养殖户扩展信息序列化器
    """
    id_card = serializers.SerializerMethodField()
    
    class Meta:
        model = FarmerProfile
        fields = '__all__'

    def get_id_card(self, obj):
        # 个人资料接口也不返回完整身份证号，仅脱敏（修改资料时可单独输入新证件号）
        return obj.masked_id_card

class AdminProfileSerializer(serializers.ModelSerializer):
    """
    管理员扩展信息序列化器
    """
    class Meta:
        model = AdminProfile
        fields = '__all__'


class UserDetailSerializer(serializers.ModelSerializer):
    """
    包含扩展信息的详细用户序列化器
    """
    profile = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'role', 'phone', 'email', 'avatar', 'profile', 'is_active', 'date_joined')

    def get_role(self, obj):
        if obj.is_staff:
            return 'admin'
        if obj.groups.filter(name='vet').exists():
            return 'vet'
        return 'farmer'

    def get_profile(self, obj):
        if obj.is_staff:
            profile = getattr(obj, 'admin_profile', None)
            return AdminProfileSerializer(profile).data if profile else None
        profile = getattr(obj, 'farmer_profile', None)
        return FarmerProfileSerializer(profile).data if profile else None

class RegisterSerializer(serializers.ModelSerializer):
    """
    注册序列化器，简化为仅需账号和密码
    """
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'password')

    def create(self, validated_data):
        username = validated_data['username']
        user = User.objects.create_user(
            username=username,
            password=validated_data['password'],
            is_active=True,  # 确保新注册用户默认处于激活状态
        )
        # 自动创建养殖户 Profile，默认名称使用用户名
        FarmerProfile.objects.create(user=user, farmer_name=username)
        return user