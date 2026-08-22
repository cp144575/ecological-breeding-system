"""
DRF 自定义权限类
================

与 ``IsAuthenticated`` 等组合使用：
``IsAdminUser``、``IsFarmerUser``（排除兽医组）、``IsVerifiedFarmer``、``IsVetUser``。
"""
from rest_framework import permissions

class IsAdminUser(permissions.BasePermission):
    """
    仅允许管理员访问 (通过 is_staff 判断)
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)

class IsFarmerUser(permissions.BasePermission):
    """
    仅允许养殖户访问 (非 is_staff)
    """
    def has_permission(self, request, view):
        user = getattr(request, 'user', None)
        return bool(
            user
            and user.is_authenticated
            and not user.is_staff
            and not user.groups.filter(name='vet').exists()
        )

class IsVerifiedFarmer(permissions.BasePermission):
    """
    仅允许已认证的养殖户访问
    """
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated and not request.user.is_staff):
            return False
        farmer_profile = getattr(request.user, 'farmer_profile', None)
        return bool(farmer_profile and getattr(farmer_profile, 'is_verified', False))


class IsVetUser(permissions.BasePermission):
    """
    仅允许兽医访问（通过用户所属分组识别）
    """

    def has_permission(self, request, view):
        user = getattr(request, 'user', None)
        if not (user and user.is_authenticated):
            return False
        if user.is_staff:
            return False
        return user.groups.filter(name='vet').exists()
