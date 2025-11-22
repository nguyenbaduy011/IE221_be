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
from django.db.models import Count
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
        
        # 1. Các chỉ số cơ bản (Giữ nguyên code cũ)
        active_courses_count = my_courses.filter(status=Course.Status.IN_PROGRESS).count()
        total_trainees = UserCourse.objects.filter(course__in=my_courses).values('user').distinct().count()
        total_supervisors = CustomUser.objects.filter(role='SUPERVISOR').count()
        
        # Completion Rate (Giữ nguyên code cũ)
        related_user_subjects = UserSubject.objects.filter(user_course__course__in=my_courses)
        total_subjects_taken = related_user_subjects.count()
        if total_subjects_taken > 0:
            finished_subjects = related_user_subjects.filter(status=2).count() 
            completion_rate = round((finished_subjects / total_subjects_taken) * 100, 2)
        else:
            completion_rate = 0.0

        # --- Dữ liệu cho Pie Chart ---
        upcoming_count = my_courses.filter(status=Course.Status.NOT_STARTED).count()
        finished_count = my_courses.filter(status=Course.Status.FINISHED).count()
        
        chart_data = [
            {"name": "Active", "value": active_courses_count, "color": "#3b82f6"},   # Blue
            {"name": "Upcoming", "value": upcoming_count, "color": "#f59e0b"},       # Amber
            {"name": "Completed", "value": finished_count, "color": "#10b981"},      # Emerald
        ]

        # --- Recent Activities  ---
        recent_joins = UserCourse.objects.filter(course__in=my_courses)\
                                         .select_related('user', 'course')\
                                         .order_by('-joined_at')[:5]
        
        activities = []
        for item in recent_joins:
            activities.append({
                "id": item.id,
                "user": item.user.full_name or item.user.email,
                "action": "joined course",
                "target": item.course.name,
                "time": item.joined_at, # Trả về ISO string, FE sẽ format thành "2 hours ago"
                "avatar": "" # Nếu user có avatar thì lấy item.user.avatar.url
            })

        return Response({
            "active_courses": active_courses_count,
            "total_trainees": total_trainees,
            "total_supervisors": total_supervisors,
            "completion_rate": completion_rate,
            "chart_data": chart_data,
            "recent_activities": activities
        }, status=status.HTTP_200_OK)