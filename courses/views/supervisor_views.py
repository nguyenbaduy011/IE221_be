from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from authen.permissions import IsAdminOrSupervisor

from courses.models.course_model import Course
from courses.serializers.course_serializer import CourseSerializer, CourseCreateSerializer
from courses.selectors import get_all_courses, get_course_by_id

from users.models.user_course import UserCourse    
from users.models.user_subject import UserSubject   
from authen.models import CustomUser

from courses.models.course_supervisor_model import CourseSupervisor
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
        print(f"DEBUG: User requesting: {user.email} (ID: {user.id})")
        
        links = CourseSupervisor.objects.filter(supervisor=user)
        print(f"DEBUG: Found {links.count()} links in CourseSupervisor table for this user.")

        course = Course.objects.filter(course_supervisors=user).distinct().order_by('-created_at')
        print(f"DEBUG: Found {course.count()} courses.")
        
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

class SupervisorDashboardStatsView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSupervisor]

    def get(self, request):
        user = request.user
        
        my_courses = Course.objects.filter(course_supervisors=user)
        
        active_courses_count = my_courses.filter(status=Course.Status.IN_PROGRESS).count()

        total_trainees = UserCourse.objects.filter(
            course__in=my_courses
        ).values('user').distinct().count()

        total_supervisors = CustomUser.objects.filter(role='SUPERVISOR').count()

        
        related_user_subjects = UserSubject.objects.filter(
            user_course__course__in=my_courses
        )
        
        total_subjects_taken = related_user_subjects.count()
        
        if total_subjects_taken > 0:
            finished_subjects = related_user_subjects.filter(status=2).count() 
            completion_rate = round((finished_subjects / total_subjects_taken) * 100, 2)
        else:
            completion_rate = 0.0

        return Response({
            "active_courses": active_courses_count,
            "total_trainees": total_trainees,
            "total_supervisors": total_supervisors,
            "completion_rate": completion_rate
        }, status=status.HTTP_200_OK)