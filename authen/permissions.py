# authen/permissions.py
from rest_framework import permissions

class IsAdminRole(permissions.BasePermission):
    """
    Chỉ cho phép user có role = 'ADMIN'
    """
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == 'ADMIN'
        )

class IsSupervisorRole(permissions.BasePermission):
    """
    Chỉ cho phép user có role = 'SUPERVISOR'
    """
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == 'SUPERVISOR'
        )

class IsTraineeRole(permissions.BasePermission):
    """
    Chỉ cho phép user có role = 'TRAINEE'
    """
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == 'TRAINEE'
        )
