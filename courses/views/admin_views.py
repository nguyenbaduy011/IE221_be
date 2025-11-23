from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response

from courses.models.course_model import Course
from courses.serializers.course_serializer import CourseSerializer, CourseCreateSerializer
from courses.selectors import get_all_courses, get_course_by_id

class AdminCourseListView(APIView):
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if getattr(request.user, 'role', None) != 'ADMIN':
             return Response(
                {"detail": "You do not have permission to view all courses."},
                status=status.HTTP_403_FORBIDDEN
            )

        courses = get_all_courses().order_by('-created_at')
        serializer = self.serializer_class(courses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
