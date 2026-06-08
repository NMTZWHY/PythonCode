from rest_framework.permissions import BasePermission

class IsAuditAdmin(BasePermission):
    """审批管理员/超级管理员才能访问"""
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.profile.role in (1, 2)

class IsSuperAdmin(BasePermission):
    """仅超级管理员"""
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.profile.role == 2