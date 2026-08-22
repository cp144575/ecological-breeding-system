"""
用户域模型
==========

- ``User``：扩展 AbstractUser（手机、头像等）。
- ``AdminProfile`` / ``FarmerProfile``：一对一扩展角色资料。
- ``Certification``：资质审核（继承 ``StatusMixin``）；身份证字段入库前经 ``encrypt_id_card``。

证件展示请始终走序列化器脱敏逻辑，勿在模板或日志中直接打印 ``id_card`` 字段原始值。
"""
from django.db import models
from django.contrib.auth.models import AbstractUser
from typing import TYPE_CHECKING, Any
from apps.core.models import StatusMixin
from apps.core.utils import encrypt_id_card, decrypt_id_card, mask_id_card

class User(AbstractUser):
    """
    基础用户模型，扩展 Django 自带的 AbstractUser
    """
    phone = models.CharField(max_length=11, unique=True, null=True, blank=True, verbose_name="手机号码")
    avatar = models.ImageField(upload_to='avatars/%Y/%m/', null=True, blank=True, verbose_name="头像")
    
    # 避免与Django内置用户模型的中间表冲突
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='custom_user_set',
        related_query_name='user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='custom_user_set',
        related_query_name='user',
    )

    class Meta:
        app_label = 'users'
        db_table = 'users_user'
        verbose_name = '用户基础信息'
        verbose_name_plural = verbose_name

class AdminProfile(models.Model):
    """
    管理员扩展信息表
    """
    if TYPE_CHECKING:
        objects: Any

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin_profile', verbose_name="关联用户")
    real_name = models.CharField(max_length=50, verbose_name="真实姓名")
    department = models.CharField(max_length=100, null=True, blank=True, verbose_name="所属部门")

    class Meta:
        db_table = 'users_admin_profile'
        verbose_name = '管理员信息'
        verbose_name_plural = verbose_name

class FarmerProfile(models.Model):
    """
    养殖户扩展信息表
    """
    if TYPE_CHECKING:
        objects: Any

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='farmer_profile', verbose_name="关联用户")
    farmer_name = models.CharField(max_length=100, verbose_name="养殖场名称/姓名")
    id_card = models.CharField(max_length=255, null=True, blank=True, verbose_name="身份证号")
    address = models.CharField(max_length=255, null=True, blank=True, verbose_name="联系地址")
    is_verified = models.BooleanField(default=False, verbose_name="是否已认证")  # type: ignore

    def save(self, *args, **kwargs):
        # 仅在 id_card 未加密时进行加密
        id_card_val = str(self.id_card) if self.id_card else ""
        if id_card_val and not id_card_val.startswith("ENC_"):
            self.id_card = encrypt_id_card(id_card_val)
        super().save(*args, **kwargs)

    @property
    def is_certified(self):
        return bool(self.is_verified)

    @property
    def decrypted_id_card(self):
        return decrypt_id_card(str(self.id_card) if self.id_card else "")

    @property
    def masked_id_card(self):
        return mask_id_card(self.decrypted_id_card)

    class Meta:
        db_table = 'users_farmer_profile'
        verbose_name = '养殖户信息'
        verbose_name_plural = verbose_name

class Certification(StatusMixin):
    """
    资格认证表 - 通用审核模型实现
    """
    if TYPE_CHECKING:
        objects: Any
        farmer: Any

    farmer = models.ForeignKey(FarmerProfile, on_delete=models.CASCADE, related_name='certifications', verbose_name="养殖户")
    id_card = models.CharField(max_length=255, verbose_name="身份证号", null=True, blank=True)
    id_card_front = models.ImageField(upload_to='certs/id_cards/', verbose_name="身份证正面")
    id_card_back = models.ImageField(upload_to='certs/id_cards/', verbose_name="身份证反面", null=True, blank=True)
    breeding_license = models.ImageField(upload_to='certs/licenses/', verbose_name="养殖许可证", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="提交时间")

    def save(self, *args, **kwargs):
        # 仅在 id_card 未加密时进行加密
        id_card_val = str(self.id_card) if self.id_card else ""
        if id_card_val and not id_card_val.startswith("ENC_"):
            self.id_card = encrypt_id_card(id_card_val)
        
        # 逻辑增强：如果认证状态变为“通过”(1)，则同步更新养殖户的认证状态
        if self.status == 1:
            # 明确指定 farmer 为 FarmerProfile 实例
            farmer_instance = self.farmer
            if farmer_instance:
                setattr(farmer_instance, 'is_verified', True)
                farmer_instance.save()
            
        super().save(*args, **kwargs)

    @property
    def decrypted_id_card(self):
        return decrypt_id_card(str(self.id_card) if self.id_card else "")

    @property
    def masked_id_card(self):
        return mask_id_card(self.decrypted_id_card)

    class Meta:
        db_table = 'users_certification'
        verbose_name = '资格认证'
        verbose_name_plural = verbose_name