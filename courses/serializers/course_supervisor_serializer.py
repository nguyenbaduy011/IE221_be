from rest_framework import serializers
from django.contrib.auth.models import User
from courses.models.course_supervisor_model import CourseSupervisor

class UserBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class CourseSupervisorSerializer(serializers.ModelSerializer):
    supervisor = UserBasicSerializer(read_only=True)

    class Meta:
        model = CourseSupervisor
        fields = ['id', 'course', 'supervisor', 'created_at']