from rest_framework import serializers
from authen.models import CustomUser
from courses.models.course_supervisor_model import CourseSupervisor

class UserBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'full_name']

class CourseSupervisorSerializer(serializers.ModelSerializer):
    supervisor = UserBasicSerializer(read_only=True)

    class Meta:
        model = CourseSupervisor
        fields = ['id', 'course', 'supervisor', 'created_at']