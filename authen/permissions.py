from rest_framework import permissions

class RolePermission(permissions.BasePermission):
    """
    Base class cho permission theo role.
    - allowed_roles: list hoặc tuple các role được phép.
    Subclass phải gán allowed_roles.
    """
    allowed_roles = []  # VD: ["ADMIN"], ["ADMIN", "SUPERVISOR"]

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role in self.allowed_roles
        )


# --- Role đơn lẻ ---
class IsAdminRole(RolePermission):
    allowed_roles = ["ADMIN"]

class IsSupervisorRole(RolePermission):
    allowed_roles = ["SUPERVISOR"]

class IsTraineeRole(RolePermission):
    allowed_roles = ["TRAINEE"]


# --- Role kết hợp (OR) ---
class IsAdminOrSupervisor(RolePermission):
    allowed_roles = ["ADMIN", "SUPERVISOR"]

class IsAdminOrTrainee(RolePermission):
    allowed_roles = ["ADMIN", "TRAINEE"]

class IsSupervisorOrTrainee(RolePermission):
    allowed_roles = ["SUPERVISOR", "TRAINEE"]

# --- Cho tất cả role (Admin, Supervisor, Trainee) ---
class IsAnyRole(RolePermission):
    allowed_roles = ["ADMIN", "SUPERVISOR", "TRAINEE"]
