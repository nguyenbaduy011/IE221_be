from rest_framework import serializers
from courses.models.course_model import Course
from users.models.user_course import UserCourse
from courses.models.course_subject import CourseSubject
from users.models.user_subject import UserSubject
from subjects.models.subject import Subject

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'name', 'link_to_course', 'image', 'start_date', 'finish_date', 'creator', 'status', 'created_at', 'updated_at']

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'name', 'max_score', 'estimated_time_days', 'created_at', 'updated_at', 'image']

class CourseSubjectSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)
    subject = SubjectSerializer(read_only=True)
    class Meta:
        model = CourseSubject
        fields = ['id', 'course', 'subject', 'position', 'start_date', 'finish_date', 'created_at', 'updated_at']