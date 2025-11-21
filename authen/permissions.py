# authen/permissions.py
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
        # 1. Cho phép xem với mọi user đã đăng nhập
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated

        # 2. Kiểm tra quyền ghi (Write)
        if not request.user or not request.user.is_authenticated:
            return False

        # Admin luôn được phép
        if request.user.role == CustomUser.Role.ADMIN:
            return True

        # Supervisor logic
        if request.user.role == CustomUser.Role.SUPERVISOR:
            # Nếu là POST (Tạo mới), cần check subject_id từ request data
            if view.action == 'create':
                subject_id = request.data.get('subject_id')
                if not subject_id:
                    return False
                return self._is_supervisor_of_subject(request.user, subject_id)
            
            # Với PUT/DELETE, logic sẽ được check ở has_object_permission
            return True
        
        return False

    def has_object_permission(self, request, view, obj):
        # Read permissions allow all
        if request.method in permissions.SAFE_METHODS:
            return True

        # Admin allow all
        if request.user.role == CustomUser.Role.ADMIN:
            return True

        # Supervisor logic cho PUT/DELETE
        if request.user.role == CustomUser.Role.SUPERVISOR:
            # obj ở đây là Task instance
            # Chúng ta cần tìm subject_id của task này
            subject_id = None
            if obj.taskable_type == Task.TaskType.SUBJECT:
                subject_id = obj.taskable_id
            # Nếu task thuộc loại khác, bạn cần logic lấy ID tương ứng
            
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
        # Lấy danh sách Course ID mà Subject này thuộc về
        course_ids = CourseSubject.objects.filter(subject_id=subject_id).values_list('course_id', flat=True)
        
        # Kiểm tra xem User có giám sát bất kỳ course nào trong list trên không
        is_supervisor = CourseSupervisor.objects.filter(
            supervisor=user,
            course_id__in=course_ids
        ).exists()
        
        return is_supervisor
    
class IsCommentOwnerOrAdmin(permissions.BasePermission):
    """
    - Xem: Authenticated Users
    - Tạo: Authenticated Users
    - Sửa: Chỉ chủ sở hữu comment
    - Xóa: Chủ sở hữu HOẶC Admin
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # SAFE_METHODS (GET, HEAD, OPTIONS) cho phép hết
        if request.method in permissions.SAFE_METHODS:
            return True

        # DELETE: Cho phép Owner hoặc Admin
        if request.method == 'DELETE':
            return obj.user == request.user or request.user.role == 'ADMIN'

        # UPDATE/PATCH: Chỉ cho phép Owner
        return obj.user == request.user