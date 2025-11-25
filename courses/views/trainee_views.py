from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response

from courses.models.course_model import Course
from courses.models.course_supervisor_model import CourseSupervisor
from users.models.user_course import UserCourse
from users.models.user_subject import UserSubject
from courses.serializers.course_serializer import CourseSerializer
from courses.serializers.course_supervisor_serializer import CourseSupervisorSerializer, UserBasicSerializer
from courses.serializers.course_serializer import UserCourseMemberSerializer
from courses.serializers.course_trainee_serializers import TraineeCourseListSerializer
from courses.selectors import get_all_courses, get_course_by_id

from courses.serializers.course_detail_serializer import TraineeCourseFullDetailSerializer

class TraineeMyCoursesView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user

        my_courses = Course.objects.filter(
            user_courses__user=user
        ).distinct().order_by('-created_at')
        
        my_courses = my_courses.prefetch_related('supervisors__supervisor')

        serializer = TraineeCourseListSerializer(
            my_courses, 
            many=True, 
            context={'request': request}
        )
        
        return Response(serializer.data, status=status.HTTP_200_OK)

class TraineeCourseDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, course_id):
        user = request.user
        
        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return Response({"detail": "Course not found"}, status=status.HTTP_404_NOT_FOUND)

        is_enrolled = UserCourse.objects.filter(user=user, course=course).exists()
        if not is_enrolled:
            return Response({"detail": "You are not enrolled in this course"}, status=status.HTTP_403_FORBIDDEN)

        serializer = TraineeCourseFullDetailSerializer(
            course, 
            context={'request': request}
        )
        
        return Response(serializer.data, status=status.HTTP_200_OK)

class CourseMembersView(APIView):
    permissions_classes = [permissions.IsAuthenticated]

    def get(self, request, course_id):
        try:
            course = get_course_by_id(course_id)
        except Course.DoesNotExist:
            return Response({"detail": "Course not found."}, status=status.HTTP_404_NOT_FOUND)
    
        course_supervisors = CourseSupervisor.objects.filter(course=course).select_related('supervisor')

        list_of_supervisors = [link.supervisor for link in course_supervisors]

        supervisors_serializer = UserBasicSerializer(list_of_supervisors, many=True)
        user_courses = UserCourse.objects.filter(course=course) 
        serializer = UserCourseMemberSerializer(user_courses, many=True) 

        return Response({"course": CourseSerializer(course).data,
                        "members": serializer.data, 
                        "supervisors": supervisors_serializer.data, 
                        "member_count": user_courses.count(),
                        "supervisor_count": course_supervisors.count()
                        }, status=status.HTTP_200_OK)