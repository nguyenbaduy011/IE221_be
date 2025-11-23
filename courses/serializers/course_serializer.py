from rest_framework import serializers
from authen.models import CustomUser
from courses.models.course_model import Course
from users.models.user_course import UserCourse
from courses.serializers.course_supervisor_serializer import CourseSupervisorSerializer

class CourseSerializer(serializers.ModelSerializer):
    supervisors = CourseSupervisorSerializer(many=True, read_only=True, source='coursesupervisor_set')

    class Meta:
        model = Course
        fields = [
            'id',
            'name',
            'link_to_course',
            'image',
            'start_date',
            'finish_date',
            'creator',
            'status',
            'created_at',
            'updated_at',
            'supervisors',
        ]

class UserCourseMemberSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.full_name', read_only=True)

    class Meta:
        model = UserCourse
        fields = ['id', 'user_name', 'status', 'joined_at']