from rest_framework import serializers, exceptions
from .models import CustomUser

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

from datetime import timedelta


class UserRegistrationSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ("email", "full_name", "role", "password")
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            email=validated_data["email"],
            full_name=validated_data["full_name"],
            role=validated_data["role"],
            password=validated_data["password"],
        )

        user.is_active = False
        user.save()

        return user


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = (
            "id",
            "email",
            "full_name",
            "role",
            "birthday",
            "gender",
            "date_joined",
        )


class ResendActivationEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    remember_me = serializers.BooleanField(write_only=True, required=False)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        if email and password:
            user = CustomUser.objects.filter(email__iexact=email).first()

            if user:
                if user.check_password(password):
                    if not user.is_active:
                        raise exceptions.AuthenticationFailed(
                            detail="ACCOUNT_NOT_ACTIVE", code="ACCOUNT_NOT_ACTIVE"
                        )

        data = super().validate(attrs)

        refresh = self.get_token(self.user)

        data["user"] = {
            "id": self.user.id,
            "email": self.user.email,
            "full_name": self.user.full_name,
            "role": self.user.role,
        }

        if attrs.get("remember_me", False):
            refresh.set_exp(lifetime=timedelta(days=30))

        data["refresh"] = str(refresh)
        data["access"] = str(refresh.access_token)

        return data


class LogoutSerializer(serializers.Serializer):


    refresh = serializers.CharField()

    default_error_messages = {"bad_token": ("Token không hợp lệ hoặc đã hết hạn")}

    def validate(self, attrs):
        self.token = attrs["refresh"]
        return attrs

    def save(self, **kwargs):
        try:
            RefreshToken(self.token).blacklist()
        except TokenError:
            self.fail("bad_token")


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)
    
    new_password_confirm = serializers.CharField(required=True, write_only=True)

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Mật khẩu cũ không chính xác.")
        return value

    def validate(self, attrs):
        if attrs["new_password"] != attrs["new_password_confirm"]:
            raise serializers.ValidationError({"new_password": "Mật khẩu xác nhận không khớp."})
        return attrs

    def save(self, **kwargs):
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save()
        return user


class AdminUserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ("id", "email", "full_name", "password", "role", "is_active")
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        is_active = validated_data.pop("is_active", True)

        user = CustomUser.objects.create_user(
            email=validated_data["email"],
            full_name=validated_data.get("full_name", ""),
            role=validated_data["role"],
            password=validated_data["password"],
        )
        user.is_active = is_active
        user.save()
        return user
