# authen/views.py
from rest_framework import viewsets, permissions, generics
from rest_framework.response import Response
from .models import CustomUser
from .serializers import UserRegistrationSerializer, UserDetailSerializer, ResendActivationEmailSerializer, MyTokenObtainPairSerializer, LogoutSerializer, ChangePasswordSerializer

from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import status
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth.tokens import default_token_generator


from .services import send_activation_email

class RegistrationViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]
    serializer_class = UserRegistrationSerializer

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.save() 
            
            try:
                send_activation_email(user, request)
            except Exception as e:
                print(f"Lỗi gửi mail: {e}")

            # === ĐÂY LÀ CÁCH SỬA ===
            # 1. Tạo một dict chứa cả data và message
            response_data = {
                "data": serializer.data,
                "message": "Đăng ký thành công! Vui lòng kiểm tra email để kích hoạt tài khoản."
            }
            # 2. Trả về dict đó
            return Response(response_data, status=status.HTTP_201_CREATED)
            # ========================

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) # Lỗi 400 đã được Exception Handler xử lý

class UserProfileView(generics.RetrieveAPIView):
    """
    API endpoint để lấy thông tin user ĐANG ĐĂNG NHẬP (GET).
    Endpoint này sẽ là: GET /auth/me/
    """
    serializer_class = UserDetailSerializer
    permission_classes = [permissions.IsAuthenticated] # Chỉ ai đã đăng nhập mới xem được

    def get_object(self):
        # Tự động trả về thông tin của user đã được xác thực (từ token)
        return self.request.user

class ActivateAccountView(APIView):

    permission_classes = [permissions.AllowAny]

    def get(self, request, uidb64, token):
        try:
            # Giải mã uid
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            user = None

        # Kiểm tra token
        if user is not None and default_token_generator.check_token(user, token):
            # Kích hoạt user
            user.is_active = True
            user.save()
            return Response({"message": "Tài khoản kích hoạt thành công!"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Link kích hoạt không hợp lệ."}, status=status.HTTP_400_BAD_REQUEST)

class ResendActivationEmailView(generics.GenericAPIView):
    """
    API endpoint để gửi lại email kích hoạt.
    POST /auth/resend-activation/
    """
    permission_classes = [permissions.AllowAny] # Ai cũng có thể gọi
    serializer_class = ResendActivationEmailSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        try:
            # 1. Tìm user bằng email
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            user = None

        # 2. Chỉ gửi mail nếu user tồn tại VÀ chưa được kích hoạt
        if user and not user.is_active:
            try:
                # 3. Tái sử dụng service cũ!
                send_activation_email(user, request)
            except Exception as e:
                # Ghi lại lỗi nếu có, nhưng không báo cho user biết
                print(f"Lỗi gửi lại mail: {e}")
        
        # 4. (Rất quan trọng - Bảo mật)
        # Luôn trả về thông báo thành công,
        # ngay cả khi email không tồn tại hoặc đã kích hoạt.
        # Điều này ngăn chặn hacker dò email ("user enumeration").
        return Response(
            {"message": "Nếu tài khoản của bạn tồn tại và chưa được kích hoạt, một email mới đã được gửi đi."},
            status=status.HTTP_200_OK
        )

class MyTokenObtainPairView(TokenObtainPairView):
    """
    View đăng nhập tùy chỉnh, sử dụng Serializer tùy chỉnh.
    """
    serializer_class = MyTokenObtainPairSerializer

class LogoutView(generics.GenericAPIView):
    """
    API endpoint để đăng xuất và blacklist refresh token.
    POST /auth/logout/
    """
    serializer_class = LogoutSerializer
    permission_classes = [permissions.IsAuthenticated] # Chỉ user đã đăng nhập mới được logout

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Trả về 204 No Content là chuẩn cho việc logout/delete
        return Response(status=status.HTTP_204_NO_CONTENT)


class ChangePasswordView(generics.UpdateAPIView):
    """
    API endpoint để đổi mật khẩu.
    PUT /auth/change-password/
    """
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated] # Bắt buộc phải đăng nhập

    def get_object(self):
        # Trả về chính user đang đăng nhập
        return self.request.user

    def update(self, request, *args, **kwargs):
        # Ghi đè phương thức update
        user = self.get_object()
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save() # Gọi hàm save() trong serializer
        
        return Response({"message": "Đổi mật khẩu thành công."}, status=status.HTTP_200_OK)