from rest_framework import serializers
from django.utils.crypto import get_random_string
from subjects.models.task import Task
from users.models.user_task import UserTask
from courses.models.course_subject import CourseSubject
from users.models.user_course import UserCourse
from users.models.user_subject import UserSubject
from authen.models import CustomUser # Import model từ authen
from authen.services import send_new_account_email
from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from users.models.comment import Comment # Import model Comment
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


# --- COMMENT SERIALIZERS (FIXED) ---
class CommentUserSerializer(serializers.ModelSerializer):
    """Serializer nhỏ chỉ để hiện tên người comment"""
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'full_name', 'role']

class CommentSerializer(serializers.ModelSerializer):
    user = CommentUserSerializer(read_only=True)
    # Client gửi lên tên model (vd: 'task', 'dailyreport') và ID của object đó
    model_name = serializers.CharField(write_only=True)
    object_id = serializers.IntegerField()

    class Meta:
        model = Comment
        fields = ['id', 'user', 'content', 'created_at', 'updated_at', 'model_name', 'object_id']
        read_only_fields = ['id', 'created_at', 'updated_at', 'user']

    def validate(self, data):
        model_name = data.get('model_name')
        object_id = data.get('object_id')

        # 1. Tìm ContentType từ tên model
        try:
            content_type = ContentType.objects.get(model=model_name.lower())
        except ContentType.DoesNotExist:
            raise serializers.ValidationError({"model_name": f"Model '{model_name}' không hợp lệ."})

        # 2. Kiểm tra object có tồn tại không
        model_class = content_type.model_class()
        if not model_class.objects.filter(id=object_id).exists():
             raise serializers.ValidationError({"object_id": "ID đối tượng không tồn tại."})
        
        # Lưu content_type vào context để dùng ở hàm create
        self.context['content_type'] = content_type
        return data

    def create(self, validated_data):
        content_type = self.context['content_type'] # Lấy từ bước validate
        model_name = validated_data.pop('model_name') # Bỏ trường ảo này đi
        
        user = self.context['request'].user
        
        comment = Comment.objects.create(
            user=user,
            content_type=content_type,
            **validated_data
        )
        return comment