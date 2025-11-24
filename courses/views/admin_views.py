from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response

from courses.models.course_model import Course
from courses.serializers.course_serializer import (
    CourseSerializer,
    CourseCreateSerializer,
)
from courses.selectors import get_all_courses, get_course_by_id


class AdminCourseListView(generics.ListAPIView):
    """
    API: GET /api/admin/courses/
    Lấy danh sách tất cả các khóa học (dành cho Admin/Supervisor)
    """

    queryset = Course.objects.all().order_by("-created_at")
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    # Nếu bạn muốn thêm tính năng tìm kiếm (Search)
    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.query_params.get("search", None)
        status_query = self.request.query_params.get("status", None)

        if search_query:
            queryset = queryset.filter(name__icontains=search_query)

        if status_query and status_query != "ALL":
            queryset = queryset.filter(status=status_query)

        return queryset


class AdminCourseDetailView(APIView):
    """
    GET /admin/courses/<int:pk>/
    Lấy chi tiết một khóa học theo ID (Chỉ dành cho ADMIN)
    """

    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    # Nếu bạn có permission IsAdmin riêng thì thêm vào đây, ví dụ: [permissions.IsAuthenticated, IsAdmin]

    def get(self, request, course_id):
        course = get_course_by_id(course_id)
        if not course:
            return Response(
                {"detail": "Course not found."}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.serializer_class(course)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, course_id):
        course = get_course_by_id(course_id)
        if not course:
            return Response(
                {"detail": "Course not found."}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.serializer_class(course, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
