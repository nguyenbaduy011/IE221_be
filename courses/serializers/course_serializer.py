from rest_framework import serializers
from django.db import transaction
from authen.models import CustomUser
from courses.models.course_model import Course
from users.models.user_course import UserCourse
from courses.models.course_supervisor_model import CourseSupervisor
from courses.serializers.course_supervisor_serializer import CourseSupervisorSerializer


class UserBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["id", "full_name"]


class CourseSupervisorSerializer(serializers.ModelSerializer):
    supervisor = UserBasicSerializer(read_only=True)

    class Meta:
        model = CourseSupervisor
        fields = ["id", "supervisor", "created_at"]


class CourseSerializer(serializers.ModelSerializer):
    supervisor_count = serializers.SerializerMethodField()
    member_count = serializers.SerializerMethodField()

    supervisors = CourseSupervisorSerializer(
        many=True, read_only=True, source="coursesupervisor_set"
    )

    class Meta:
        model = Course
        fields = [
            "id",
            "name",
            "link_to_course",
            "image",
            "start_date",
            "finish_date",
            "status",
            "created_at",
            "updated_at",
            "supervisors",
            "supervisor_count",
            "member_count",
        ]

    def get_supervisor_count(self, obj):
        return CourseSupervisor.objects.filter(course=obj).count()

    def get_member_count(self, obj):
        return UserCourse.objects.filter(course=obj).count()


class CourseCreateSerializer(serializers.ModelSerializer):
    subjects = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
    )
    supervisors = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
    )

    class Meta:
        model = Course
        fields = [
            "name",
            "link_to_course",
            "image",
            "start_date",
            "finish_date",
            "status",
            "subjects",
            "supervisors",
        ]

    def validate_subjects(self, value):
        from subjects.models.subject import Subject

        for subject_id in value:
            if not Subject.objects.filter(id=subject_id).exists():
                raise serializers.ValidationError(
                    f"Subject with id {subject_id} does not exist."
                )
        return value

    def validate_supervisors(self, value):
        for sid in value:
            if not CustomUser.objects.filter(id=sid, role="supervisor").exists():
                raise serializers.ValidationError(
                    f"User {sid} is not a valid supervisor."
                )
        return value


class UserCourseMemberSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.full_name", read_only=True)

    class Meta:
        model = UserCourse
        fields = ["id", "user_name", "status", "joined_at"]
