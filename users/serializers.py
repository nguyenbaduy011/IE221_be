from rest_framework import serializers
from django.utils.crypto import get_random_string
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