from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response

from courses.models.course_model import Course
from courses.serializers.course_serializer import CourseSerializer
from courses.selectors import get_all_courses, get_course_by_id

class IsSupervisor(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and getattr(request.user, 'role', None) in ['supervisor', 'admin']

class SupervisorCourseListView(APIView):
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated, IsSupervisor]

    def get(self, request):
        user = self.request.user
        """
        Lấy danh sách khóa học do supervisor quản lý
        """
        if getattr(user, 'role', None) == 'admin':
            courses = get_all_courses()
        else:
            courses = Course.objects.filter(course_supervisors__supervisor=user)

        serializer = self.serializer_class(courses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class SupervisorCourseDetailView(APIView):
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated, IsSupervisor]

    def get(self, request, course_id):
        user = self.request.user
        course = get_course_by_id(course_id)
        if not course:
            return Response({"detail": "Course not found."}, status=status.HTTP_404_NOT_FOUND)

        if getattr(user, 'role', None) != 'admin' and not course.course_supervisors.filter(supervisor=user).exists():
            return Response({"detail": "You do not have permission to view this course."}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.serializer_class(course)
        return Response(serializer.data, status=status.HTTP_200_OK)