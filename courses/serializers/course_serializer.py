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

class CourseCreateSerializer(serializers.ModelSerializer):
    subjects = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False
    )

    class Meta:
        model = Course
        fields = [
            'name',
            'link_to_course',
            'image',
            'start_date',
            'finish_date',
            'status',
            'subjects',
        ]
    
    def validate_subjects(self, value):
        from subjects.models.subject import Subject
        for subject_id in value:
            if not Subject.objects.filter(id=subject_id).exists():
                raise serializers.ValidationError(f"Subject with id {subject_id} does not exist.")
        return value

    def validate_supervisors(self, value):
        for supervisor_id in value:
            if not CustomUser.objects.filter(id=supervisor_id, role__in=['supervisor']).exists():
                raise serializers.ValidationError(f"User with id {supervisor_id} is not a valid supervisor.")
        return value

class UserCourseMemberSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.full_name', read_only=True)

    class Meta:
        model = UserCourse
        fields = ['id', 'user_name', 'status', 'joined_at']