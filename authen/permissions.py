from rest_framework import permissions

from authen.models import CustomUser
from courses.models.course_subject import CourseSubject
from courses.models.course_supervisor_model import CourseSupervisor
from subjects.models.task import Task

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

class IsAdminOrSupervisor(permissions.BasePermission):
    """
    Cho phép truy cập nếu user là ADMIN hoặc SUPERVISOR
    """
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role in ['ADMIN', 'SUPERVISOR']
        )

class IsTaskEditor(permissions.BasePermission):
    """
    - SAFE_METHODS (GET, HEAD, OPTIONS): Cho phép tất cả Authenticated Users.
    - Write (POST, PUT, DELETE):
        + Admin: Luôn cho phép.
        + Supervisor: Phải đang giám sát (CourseSupervisor) một khóa học (Course)
                      mà khóa học đó có chứa Subject của Task này.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated

        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.role == CustomUser.Role.ADMIN:
            return True

        if request.user.role == CustomUser.Role.SUPERVISOR:
            if view.action == 'create':
                subject_id = request.data.get('subject_id')
                if not subject_id:
                    return False
                return self._is_supervisor_of_subject(request.user, subject_id)

            return True

        return False

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        if request.user.role == CustomUser.Role.ADMIN:
            return True

        if request.user.role == CustomUser.Role.SUPERVISOR:
            subject_id = None
            if obj.taskable_type == Task.TaskType.SUBJECT:
                subject_id = obj.taskable_id

            if subject_id:
                return self._is_supervisor_of_subject(request.user, subject_id)

        return False

    def _is_supervisor_of_subject(self, user, subject_id):
        """
        Kiểm tra xem User có phải là Supervisor của bất kỳ Course nào
        chứa Subject này không.
        Query:
        1. Tìm các Course chứa Subject này (qua CourseSubject).
        2. Tìm xem User có trong CourseSupervisor của các Course đó không.
        """
        course_ids = CourseSubject.objects.filter(subject_id=subject_id).values_list('course_id', flat=True)

        is_supervisor = CourseSupervisor.objects.filter(
            supervisor=user,
            course_id__in=course_ids
        ).exists()

        return is_supervisor


class IsCommentOwnerOrAdmin(permissions.BasePermission):
    """
    - Xem (GET): Cho phép mọi user đã đăng nhập.
    - Tạo (POST): Cho phép mọi user đã đăng nhập.
    - Sửa (PUT/PATCH): Chỉ chủ sở hữu (người tạo comment).
    - Xóa (DELETE): Chủ sở hữu HOẶC Admin.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        if request.method == 'DELETE':
            return obj.user == request.user or request.user.role == 'ADMIN'

        return obj.user == request.user

class IsOwner(permissions.BasePermission):
    """
    Chỉ cho phép chủ sở hữu của object thực hiện thao tác
    """
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
