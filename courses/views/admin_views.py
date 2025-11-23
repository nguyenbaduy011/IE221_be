from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response

from courses.models.course_model import Course
from courses.serializers.course_serializer import (
    CourseSerializer,
    CourseCreateSerializer,
)
from courses.selectors import get_all_courses, get_course_by_id


class AdminCourseListView(APIView):
    """
    GET /admin/courses/
    Lấy tất cả các khóa học trong hệ thống (Chỉ dành cho ADMIN)
    """

    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]
    # Nếu bạn có permission IsAdmin riêng thì thêm vào đây, ví dụ: [permissions.IsAuthenticated, IsAdmin]

    def get(self, request):
        # Kiểm tra role Admin (dựa trên logic check role trong code cũ của bạn)
        if getattr(request.user, "role", None) != "ADMIN":
            return Response(
                {"detail": "You do not have permission to view all courses."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Sử dụng selector get_all_courses đã có
        courses = get_all_courses().order_by("-created_at")
        serializer = self.serializer_class(courses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AdminCourseDetailView(APIView):
    """
    GET /admin/courses/<int:pk>/
    Lấy chi tiết một khóa học theo ID (Chỉ dành cho ADMIN)
    """

    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    # Nếu bạn có permission IsAdmin riêng thì thêm vào đây, ví dụ: [permissions.IsAuthenticated, IsAdmin]

    def get(self, course_id):
        course = get_course_by_id(course_id)
        if not course:
            return Response(
                {"detail": "Course not found."}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.serializer_class(course)
        return Response(serializer.data, status=status.HTTP_200_OK)
