from rest_framework import serializers
from django.utils.crypto import get_random_string
from subjects.models.task import Task
from users.models.user_task import UserTask
from courses.models.course_subject import CourseSubject
from users.models.user_course import UserCourse
from users.models.user_subject import UserSubject
from authen.models import CustomUser # Import model từ authen
from authen.services import send_new_account_email
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
    # Cho phép client gửi ID nhưng response trả về thông tin chi tiết nếu cần
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
        """
        Validate logic ràng buộc giữa UserCourse và CourseSubject
        """
        user = self.context['request'].user
        user_course = data.get('user_course')
        course_subject = data.get('course_subject')

        # 1. Kiểm tra xem UserCourse có thuộc về User hiện tại không (nếu tạo mới)
        if user_course and user_course.user != user:
             raise serializers.ValidationError("UserCourse does not belong to this user.")

        # 2. Kiểm tra xem CourseSubject có thuộc về Course trong UserCourse không
        if user_course and course_subject:
            if course_subject.course != user_course.course:
                raise serializers.ValidationError("The selected Subject does not belong to this Course.")
        
        return data


# --- USER TASK SERIALIZERS ---

class UserTaskSerializer(serializers.ModelSerializer):
    task_id = serializers.PrimaryKeyRelatedField(
        queryset=Task.objects.all(), source='task', write_only=True
    )
    user_subject_id = serializers.PrimaryKeyRelatedField(
        queryset=UserSubject.objects.all(), source='user_subject', write_only=True
    )

    class Meta:
        model = UserTask
        fields = [
            'id',
            'task_id',
            'task',
            'user_subject_id',
            'user_subject',
            'status',
            'spent_time',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'task', 'user_subject']

    def validate(self, data):
        """
        Validate logic: Task phải liên quan đến Subject của UserSubject
        """
        user = self.context['request'].user
        user_subject = data.get('user_subject')
        task = data.get('task')
        
        # 1. Kiểm tra UserSubject có thuộc về User không
        if user_subject and user_subject.user != user:
            raise serializers.ValidationError("UserSubject does not belong to this user.")

        # 2. Logic kiểm tra Task có thuộc về Subject/CourseSubject này không (Optional/Advanced)
        # Lưu ý: Do Task là polymorphic (thuộc Subject hoặc CourseSubject) nên logic check sẽ khá phức tạp.
        # Ở mức cơ bản, ta check xem UserSubject đã Active chưa.
        if user_subject and user_subject.status == UserSubject.Status.NOT_STARTED:
             raise serializers.ValidationError("Cannot start a task for a subject that has not started.")

        return data