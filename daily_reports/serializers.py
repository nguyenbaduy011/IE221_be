from rest_framework import serializers
from .models import DailyReport

class DailyReportSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source='course.name', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = DailyReport
        fields = [
            'id', 'user', 'course', 'course_name',
            'content', 'status', 'created_at', 'updated_at', 'user_name'
        ]
