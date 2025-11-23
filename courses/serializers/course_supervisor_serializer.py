from rest_framework import serializers
from django.db import transaction

from authen.models import CustomUser
from courses.models.course_supervisor_model import CourseSupervisor
from courses.models.course_model import Course
from subjects.models.subject import Subject
from users.models.comment import Comment

class UserBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["id", "full_name"]

class CourseSupervisorSerializer(serializers.ModelSerializer):
    supervisor = UserBasicSerializer(read_only=True)

    class Meta:
        model = CourseSupervisor
        fields = ["id", "course", "supervisor", "created_at"]


class AddSubjectTaskSerializer(serializers.Serializer):
    subject_id = serializers.IntegerField(required=False, allow_null=True)
    name = serializers.CharField(required=False, max_length=100)
    max_score = serializers.IntegerField(required=False)
    estimated_time_days = serializers.IntegerField(required=False)
    image = serializers.ImageField(required=False)
    tasks = serializers.ListField(
        child=serializers.CharField(max_length=255),
        required=False,
        default=list,
    )

    def validate(self, data):
        subject_id = data.get("subject_id")

        if not subject_id:
            if not data.get("name"):
                raise serializers.ValidationError("Name is required for new subject.")
            if not data.get("max_score"):
                raise serializers.ValidationError("Max score is required.")
            if not data.get("estimated_time_days"):
                raise serializers.ValidationError("Estimated time is required.")
        else:
            if not Subject.objects.filter(id=subject_id).exists():
                raise serializers.ValidationError("Subject ID does not exist.")

        return data


class AddTraineeSerializer(serializers.Serializer):
    trainee_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=CustomUser.objects.filter(role="TRAINEE"),
    )

    def validate_trainee_ids(self, value):
        for trainee in value:
            if trainee.role != CustomUser.Role.TRAINEE:
                raise serializers.ValidationError(
                    f"User with ID {trainee.id} is not a trainee."
                )
        return value


class AddSupervisorSerializer(serializers.Serializer):
    supervisor_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=CustomUser.objects.filter(role="SUPERVISOR")
    )

class DeleteIDSerializer(serializers.Serializer):
    id = serializers.IntegerField()

class CommentHistorySerializer(serializers.ModelSerializer):
    user = UserBasicSerializer(read_only=True)
    class Meta:
        model = Comment
        fields = ['id', 'user', 'content', 'created_at']