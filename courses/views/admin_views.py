from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from authen.permissions import IsAdminRole
from users.models.user_course import UserCourse
from users.models.user_subject import UserSubject
from authen.models import CustomUser

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

class AdminDashboardStatsView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminRole]

    def get(self, request):
        all_courses = Course.objects.all()

        active_courses_count = all_courses.filter(
            status=Course.Status.IN_PROGRESS
        ).count()
        upcoming_count = all_courses.filter(status=Course.Status.NOT_STARTED).count()
        finished_count = all_courses.filter(status=Course.Status.FINISHED).count()
        supervisor_count = CustomUser.objects.filter(role=CustomUser.Role.SUPERVISOR).count()
        total_trainees = (
            UserCourse.objects.values("user")
            .distinct()
            .count()
        )

        related_user_subjects = UserSubject.objects.all()
        total_subjects_taken = related_user_subjects.count()
        finished_subjects = (
            related_user_subjects.filter(
                status__in=[
                    UserSubject.Status.FINISHED_EARLY,
                    UserSubject.Status.FINISHED_ON_TIME,
                    UserSubject.Status.FINISED_BUT_OVERDUE,
                ]
            ).count()
            if total_subjects_taken > 0
            else 0
        )

        completion_rate = (
            round((finished_subjects / total_subjects_taken) * 100, 2)
            if total_subjects_taken
            else 0.0
        )

        chart_data = [
            {"name": "Active", "value": active_courses_count, "color": "#3b82f6"},
            {"name": "Upcoming", "value": upcoming_count, "color": "#f59e0b"},
            {"name": "Completed", "value": finished_count, "color": "#10b981"},
        ]

        recent_joins = (
            UserCourse.objects.select_related("user", "course")
            .order_by("-joined_at")[:5]
        )

        activities = [
            {
                "id": item.id,
                "user": item.user.full_name or item.user.email,
                "action": "joined course",
                "target": item.course.name,
                "time": item.joined_at,
                "avatar": "",
            }
            for item in recent_joins
        ]

        return Response(
            {
                "active_courses": active_courses_count,
                "total_trainees": total_trainees,
                "completion_rate": completion_rate,
                "chart_data": chart_data,
                "recent_activities": activities,
                "total_supervisors": supervisor_count
            },
            status=status.HTTP_200_OK,
        )
