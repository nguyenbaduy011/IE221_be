from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from authen.permissions import IsAdminOrSupervisor

from courses.models.course_model import Course
from courses.serializers.course_serializer import CourseSerializer, CourseCreateSerializer
from courses.selectors import get_all_courses, get_course_by_id

class SupervisorCourseListView(APIView):
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSupervisor]

    def get(self, request):
        courses = get_all_courses().order_by('-created_at')
        serializer = self.serializer_class(courses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class SupervisorMyCourseListView(APIView):
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSupervisor]

    def get(self, request):
        user = self.request.user
        course = Course.objects.filter(course_supervisors=user).distinct().order_by('-created_at')
        return Response(self.serializer_class(course, many=True).data, status=status.HTTP_200_OK)

class SupervisorCourseDetailView(APIView):
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSupervisor]

    def get(self, request, course_id):
        user = self.request.user
        course = get_course_by_id(course_id)
        if not course:
            return Response({"detail": "Course not found."}, status=status.HTTP_404_NOT_FOUND)

        if getattr(user, 'role', None) != 'ADMIN' and not course.course_supervisors.filter(supervisor=user).exists():
            return Response({"detail": "You do not have permission to view this course."}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.serializer_class(course)
        return Response(serializer.data, status=status.HTTP_200_OK)

class SupervisorCourseCreateView(APIView):
    serializer_class = CourseCreateSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSupervisor]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        course = CourseCreateService.create_course(user=request.user, validated_data=serializer.validated_data)
        response_serializer = self.serializer_class(course)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
