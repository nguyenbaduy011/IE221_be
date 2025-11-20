from rest_framework import serializers
from .models import DailyReport
from django.utils import timezone

class DailyReportSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source='course.name', read_only=True)
    user_name = serializers.CharField(source='user.full_name', read_only=True)

    class Meta:
        model = DailyReport
        fields = [
            'id', 'user', 'course', 'course_name',
            'content', 'status', 'created_at', 'updated_at', 'user_name'
        ]

        extra_kwargs = {
            'user': {'read_only': True},
            'course': {'required': True},
        }

    def validate(self, data):
        request = self.context.get('request')
        if not request or not request.user:
            return data

        user = request.user
        course = data.get('course')

        today = timezone.now().date()

        exists_query = DailyReport.objects.filter(
            user=user,
            course=course,
            created_at__date=today
        )

        if self.instance:
            exists_query = exists_query.exclude(pk=self.instance.pk)

        if exists_query.exists():
            raise serializers.ValidationError(
                {"course": "Bạn đã tạo báo cáo cho khóa học này ngày hôm nay rồi."}
            )

        return data
