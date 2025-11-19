# authen/views.py
from rest_framework import viewsets, permissions, generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.exceptions import ValidationError, NotFound

from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth.tokens import default_token_generator

from .models import CustomUser
from .permissions import IsAdminRole
from .serializers import (
    UserRegistrationSerializer, 
    UserDetailSerializer, 
    ResendActivationEmailSerializer, 
    MyTokenObtainPairSerializer, 
    LogoutSerializer, 
    ChangePasswordSerializer,
)
from .services import send_activation_email

class RegistrationViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]
    serializer_class = UserRegistrationSerializer

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        
        # Thêm raise_exception=True. 
        # Nếu lỗi, nó sẽ tự ném ValidationError -> custom_exception_handler sẽ bắt và format lại.
        serializer.is_valid(raise_exception=True) 
        
        # Nếu chạy xuống được đây nghĩa là dữ liệu đã đúng (không cần indentation trong if nữa)
        user = serializer.save()
        
        try:
            send_activation_email(user, request)
        except Exception as e:
            print(f"Lỗi gửi mail: {e}")

        return Response({
            "data": serializer.data,
            "message": "Đăng ký thành công! Vui lòng kiểm tra email để kích hoạt."
        }, status=status.HTTP_201_CREATED)

class UserProfileView(generics.RetrieveAPIView):
    """
    GET /auth/me/
    Renderer sẽ tự động bọc thành: { status: success, data: {...}, message: "Thành công" }
    """
    serializer_class = UserDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

class ActivateAccountView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            user = None

        # --- SỬA LỖI LOGIC Ở ĐÂY ---
        # Bạn phải kiểm tra user và token, chứ không dùng biến 'success' chưa định nghĩa
        if user is not None and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            # Renderer sẽ biến cái này thành: { status: success, message: "...", data: null }
            return Response({"message": "Tài khoản kích hoạt thành công!"}, status=status.HTTP_200_OK)

        raise ValidationError({"token": "Link kích hoạt không hợp lệ hoặc đã hết hạn."})

class ResendActivationEmailView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = ResendActivationEmailSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            user = None

        if user and not user.is_active:
            try:
                send_activation_email(user, request)
            except Exception as e:
                print(f"Lỗi gửi lại mail: {e}")
        
        # Renderer xử lý message này
        return Response(
            {"message": "Nếu tài khoản tồn tại và chưa kích hoạt, email mới đã được gửi."},
            status=status.HTTP_200_OK
        )

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
    # View này trả về dict (access, refresh, user).
    # Renderer sẽ bọc nó vào 'data'.

class LogoutView(generics.GenericAPIView):
    serializer_class = LogoutSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # LƯU Ý: Đổi sang 200 OK và có message để Frontend dễ xử lý đồng nhất
        return Response({"message": "Đăng xuất thành công."}, status=status.HTTP_200_OK)

class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        super().update(request, *args, **kwargs)
        # Renderer sẽ xử lý message này
        return Response({"message": "Đổi mật khẩu thành công."}, status=status.HTTP_200_OK)
