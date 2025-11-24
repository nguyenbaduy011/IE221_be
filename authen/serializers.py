# authen/serializers.py
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
        # Băm (hash) mật khẩu trước khi lưu
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
    """
    Serializer để hiển thị thông tin chi tiết của user (an toàn).
    """

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
    """
    Serializer tùy chỉnh:
    1. Kiểm tra user chưa active -> Trả lỗi ACCOUNT_NOT_ACTIVE
    2. Thêm 'remember_me' để chỉnh thời hạn token.
    3. Thêm thông tin user vào response.
    """

    remember_me = serializers.BooleanField(write_only=True, required=False)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        if email and password:
            # Tìm user trong DB
            user = CustomUser.objects.filter(email__iexact=email).first()

            if user:
                # Kiểm tra mật khẩu thủ công
                if user.check_password(password):
                    # Nếu mật khẩu đúng, kiểm tra tiếp is_active
                    if not user.is_active:
                        # NẾU CHƯA ACTIVE: Ném lỗi với code riêng biệt
                        raise exceptions.AuthenticationFailed(
                            detail="ACCOUNT_NOT_ACTIVE", code="ACCOUNT_NOT_ACTIVE"
                        )
                # Nếu mật khẩu sai: Để im, hàm super().validate() phía dưới sẽ lo việc báo lỗi
        # ----------------------

        # Chạy hàm validate gốc của SimpleJWT
        # Hàm này sẽ kiểm tra user/pass lần nữa và tạo token nếu mọi thứ OK (bao gồm is_active=True)
        data = super().validate(attrs)

        # Lấy đối tượng refresh token
        refresh = self.get_token(self.user)

        # Thêm thông tin user vào Access Token response
        data["user"] = {
            "id": self.user.id,
            "email": self.user.email,
            "full_name": self.user.full_name,
            "role": self.user.role,
        }

        # Xử lý Remember Me
        if attrs.get("remember_me", False):
            refresh.set_exp(lifetime=timedelta(days=30))

        data["refresh"] = str(refresh)
        data["access"] = str(refresh.access_token)

        return data


class LogoutSerializer(serializers.Serializer):
    """
    Serializer để nhận refresh token và đưa vào blacklist.
    """

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
    """
    Serializer để đổi mật khẩu (cho user đã đăng nhập).
    """

    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)
    # Bạn có thể thêm 'new_password_confirm' nếu muốn

    def validate_old_password(self, value):
        # Lấy user từ context (được truyền vào từ View)
        user = self.context["request"].user

        if not user.check_password(value):
            raise serializers.ValidationError("Mật khẩu cũ không chính xác.")
        return value

    def validate(self, attrs):
        if attrs["new_password"] != attrs["new_password_confirm"]:
            raise serializers.ValidationError({"new_password": "Mật khẩu không khớp."})
        return attrs

    def save(self, **kwargs):
        # Lưu mật khẩu mới
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save()
        return user


class AdminUserCreateSerializer(serializers.ModelSerializer):
    """
    Serializer cho Admin tạo User mới:
    - Không cần confirm password (giả định Admin set cứng hoặc auto).
    - Set is_active = True mặc định (hoặc tuỳ chọn).
    - Cho phép chọn Role ngay lập tức.
    """

    class Meta:
        model = CustomUser
        fields = ("id", "email", "full_name", "password", "role", "is_active")
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        # Mặc định Admin tạo thì cho active luôn, trừ khi Admin cố tình set False
        is_active = validated_data.pop("is_active", True)

        user = CustomUser.objects.create_user(
            email=validated_data["email"],
            full_name=validated_data.get("full_name", ""),
            role=validated_data["role"],  # Admin được quyền gán role
            password=validated_data["password"],
        )
        user.is_active = is_active
        user.save()
        return user
