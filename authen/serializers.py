# authen/serializers.py
from rest_framework import serializers
from .models import CustomUser

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from datetime import timedelta

class UserRegistrationSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ('email', 'full_name', 'role', 'password')
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        # Băm (hash) mật khẩu trước khi lưu
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            full_name=validated_data['full_name'],
            role=validated_data['role'],
            password=validated_data['password']
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
        fields = ('id', 'email', 'full_name', 'role', 'birthday', 'gender', 'date_joined')

class ResendActivationEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Serializer tùy chỉnh để thêm 'remember_me' và thay đổi thời hạn token.
    """
    # Thêm trường 'remember_me' vào, nó không cần lưu vào model
    remember_me = serializers.BooleanField(write_only=True, required=False)

    def validate(self, attrs):
        # Chạy hàm validate() của lớp cha (để xác thực user, pass)
        data = super().validate(attrs)

        # Lấy đối tượng refresh token
        refresh = self.get_token(self.user)

        # Thêm thông tin user vào Access Token (tùy chọn, nhưng rất tiện)
        data['user'] = {
            'id': self.user.id,
            'email': self.user.email,
            'full_name': self.user.full_name,
            'role': self.user.role
        }

        # Kiểm tra xem 'remember_me' có được gửi và có = True không
        if attrs.get('remember_me', False):
            # Nếu có, set thời hạn của Refresh Token là 30 ngày
            refresh.set_exp(lifetime=timedelta(days=30))
        
        # (Nếu không, nó sẽ tự dùng thời hạn mặc định trong settings.py)

        # Cập nhật lại token trong data trả về
        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)

        return data