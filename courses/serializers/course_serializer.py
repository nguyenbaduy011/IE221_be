from rest_framework import serializers
from authen.models import CustomUser
from courses.models.course_model import Course
from users.models.user_course import UserCourse
from courses.models.course_supervisor_model import CourseSupervisor
from courses.serializers.course_supervisor_serializer import CourseSupervisorSerializer

class CourseSerializer(serializers.ModelSerializer):
    # --- QUAN TRỌNG: PHẢI KHAI BÁO DÒNG NÀY ---
    # Để Django biết đây là trường tính toán, không phải cột DB
    supervisor_count = serializers.SerializerMethodField()
    member_count = serializers.SerializerMethodField()
    # ------------------------------------------

    # Giữ nguyên logic supervisors cũ của bạn
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
            'status',
            'created_at',
            'updated_at',
            'supervisors',
            'supervisor_count', 
            'member_count',
        ]

class UserCourseMemberSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.full_name', read_only=True)

    class Meta:
        model = UserCourse
        fields = ['id', 'user_name', 'status', 'joined_at']