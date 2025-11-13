from rest_framework import serializers
from django.contrib.auth.models import User
from courses.models.course_model import Course
from courses.serializers.course_supervisor_serializer import CourseSupervisorSerializer

class CourseSerializer(serializers.ModelSerializer):
    supervisors = CourseSupervisorSerializer(many=True, read_only=True, source='course_supervisors')

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
