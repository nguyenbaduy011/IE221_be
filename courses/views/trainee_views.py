from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response

from courses.models.course_model import Course
from courses.serializers.course_serializer import CourseSerializer
from courses.selectors import get_all_courses, get_course_by_id

class IsTrainee(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and getattr(request.user, 'role', None) == 'trainee'

class TraineeCourseDetailView(APIView):
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated, IsTrainee]

    def get(self, request, course_id):
        course = get_course_by_id(course_id)
        if not course:
            return Response({"detail": "Course not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(course)
        return Response(serializer.data, status=status.HTTP_200_OK)