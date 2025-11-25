from rest_framework import serializers
from django.utils.crypto import get_random_string
from subjects.models.task import Task
from users.models.user_task import UserTask
from courses.models.course_subject import CourseSubject
from users.models.user_course import UserCourse
from users.models.user_subject import UserSubject
from authen.models import CustomUser
from authen.services import send_new_account_email
from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from users.models.comment import Comment
from authen.models import CustomUser

class AdminUserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'full_name', 'role', 'birthday', 'gender', 'is_active', 'is_staff', 'date_joined')

class AdminUserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'full_name', 'role', 'is_active')

    def create(self, validated_data):
        is_active = validated_data.pop('is_active', True)

        random_password = get_random_string(length=10)

        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            full_name=validated_data.get('full_name', ''),
            role=validated_data['role'],
            password=random_password
        )
        user.is_active = is_active
        user.save()

        try:
            send_new_account_email(user, random_password)
        except Exception as e:
            print(f"Lỗi gửi email cấp tài khoản: {e}")

        return user

class AdminUserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'full_name', 'role', 'is_active', 'birthday', 'gender', 'is_staff')
        read_only_fields = ('email',)

class AdminUserBulkCreateSerializer(serializers.Serializer):
    emails = serializers.ListField(
        child=serializers.EmailField(),
        allow_empty=False,
        help_text="Danh sách email"
    )
    role = serializers.ChoiceField(choices=CustomUser.Role.choices, default="TRAINEE")

    def create(self, validated_data):
        created_users = []

        for email in validated_data["emails"]:
            random_name = email.split("@")[0]
            random_password = get_random_string(10)

            user = CustomUser.objects.create_user(
                email=email,
                full_name=random_name,
                role=validated_data["role"],
                password=random_password
            )
            user.is_active = True
            user.save()

            try:
                send_new_account_email(user, random_password)
            except Exception as e:
                print(f"Failed to send email to {email}: {e}")

            created_users.append(user)
        return created_users


class UserSubjectSerializer(serializers.ModelSerializer):
    user_course_id = serializers.PrimaryKeyRelatedField(
        queryset=UserCourse.objects.all(), source='user_course', write_only=True
    )
    course_subject_id = serializers.PrimaryKeyRelatedField(
        queryset=CourseSubject.objects.all(), source='course_subject', write_only=True
    )

    class Meta:
        model = UserSubject
        fields = [
            'id',
            'user_course_id',
            'user_course',
            'course_subject_id',
            'course_subject',
            'status',
            'score',
            'started_at',
            'completed_at',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'started_at', 'completed_at', 'created_at', 'updated_at', 'user_course', 'course_subject']

    def validate(self, data):
        user = self.context['request'].user
        user_course = data.get('user_course')
        course_subject = data.get('course_subject')

        if user_course and user_course.user != user:
             raise serializers.ValidationError("UserCourse does not belong to this user.")

        if user_course and course_subject:
            if course_subject.course != user_course.course:
                raise serializers.ValidationError("The selected Subject does not belong to this Course.")

        return data


class CommentUserSerializer(serializers.ModelSerializer):
    """Serializer nhỏ chỉ để hiện tên người comment"""
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'full_name', 'role']

class CommentSerializer(serializers.ModelSerializer):
    user = CommentUserSerializer(read_only=True)
    model_name = serializers.CharField(write_only=True)
    object_id = serializers.IntegerField()

    class Meta:
        model = Comment
        fields = ['id', 'user', 'content', 'created_at', 'updated_at', 'model_name', 'object_id']
        read_only_fields = ['id', 'created_at', 'updated_at', 'user']

    def validate(self, data):
        model_name = data.get('model_name')
        object_id = data.get('object_id')

        try:
            content_type = ContentType.objects.get(model=model_name.lower())
        except ContentType.DoesNotExist:
            raise serializers.ValidationError({"model_name": f"Model '{model_name}' không hợp lệ."})

        model_class = content_type.model_class()
        if not model_class.objects.filter(id=object_id).exists():
             raise serializers.ValidationError({"object_id": "ID đối tượng không tồn tại."})

        self.context['content_type'] = content_type
        return data

    def create(self, validated_data):
        content_type = self.context['content_type']
        model_name = validated_data.pop('model_name')

        user = self.context['request'].user

        comment = Comment.objects.create(
            user=user,
            content_type=content_type,
            **validated_data
        )
        return comment


class TraineeTaskUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserTask
        fields = ['id', 'status', 'spent_time', 'submission_file']
        extra_kwargs = {
            'submission_file': {'required': False},
            'spent_time': {'required': False}
        }

    def validate_spent_time(self, value):
        if value is not None:
            return round(value, 1)
        return value


class TraineeTaskDetailSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='task.name', read_only=True)

    class Meta:
        model = UserTask
        fields = ['id', 'name', 'status', 'spent_time', 'submission_file']

class TraineeEnrolledSubjectSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='course_subject.subject.name', read_only=True)
    max_score = serializers.IntegerField(source='course_subject.subject.max_score', read_only=True)
    estimated_time_days = serializers.IntegerField(source='course_subject.subject.estimated_time_days', read_only=True)

    start_date = serializers.DateField(source='course_subject.start_date', read_only=True)
    deadline = serializers.DateField(source='course_subject.finish_date', read_only=True)
    actual_start_day = serializers.DateTimeField(source='started_at', required=False)
    actual_end_day = serializers.DateTimeField(source='completed_at', required=False)

    formatted_score = serializers.SerializerMethodField()
    duration_text = serializers.SerializerMethodField()


    tasks = TraineeTaskDetailSerializer(source='user_tasks', many=True, read_only=True)

    comments = serializers.SerializerMethodField()

    student = serializers.SerializerMethodField()
    course = serializers.SerializerMethodField()

    class Meta:
        model = UserSubject
        fields = [
            'id',
            'subject_name',
            'status',
            'score', 'max_score', 'formatted_score',
            'estimated_time_days', 'duration_text',
            'start_date', 'deadline',
            'actual_start_day', 'actual_end_day',
            'tasks', 'comments', 'student', 'course'
        ]

    def get_formatted_score(self, obj):
        current_score = obj.score if obj.score is not None else "--"
        max_score = obj.course_subject.subject.max_score
        return f"{current_score}/{max_score}"

    def get_duration_text(self, obj):
        days = obj.course_subject.subject.estimated_time_days
        return f"(Time: {days} day)"

    def get_comments(self, obj):
        content_type = ContentType.objects.get_for_model(UserSubject)
        comments = Comment.objects.filter(content_type=content_type, object_id=obj.id).order_by('-created_at')
        return CommentSerializer(comments, many=True).data

    def get_student(self, obj):
        return {
            "name": obj.user.full_name,
        }

    def get_course(self, obj):
        return {
            "name": obj.user_course.course.name,
            "start_date": obj.user_course.course.start_date,
            "finish_date": obj.user_course.course.finish_date,
            "status": obj.user_course.status
        }
