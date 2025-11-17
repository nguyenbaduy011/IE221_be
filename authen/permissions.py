# authen/permissions.py
from rest_framework import permissions

class IsAdminRole(permissions.BasePermission):
    """
    Chỉ cho phép user có role là ADMIN truy cập.
    """
    def has_permission(self, request, view):
        # Phải đăng nhập VÀ role là ADMIN
        return request.user and request.user.is_authenticated and request.user.role == 'ADMIN'