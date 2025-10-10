from rest_framework import serializers
from course.models import Courses

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Courses
        fields = '__all__' # Lấy tất cả các trường của model Courses