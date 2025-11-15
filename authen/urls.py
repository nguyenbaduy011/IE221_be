# authen/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegistrationViewSet, UserProfileView, ActivateAccountView, ResendActivationEmailView, MyTokenObtainPairView

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    
)


# Router tự động tạo URL cho 'create' (POST)
router = DefaultRouter()
router.register(r'register', RegistrationViewSet, basename='register')

urlpatterns = [
    # Tự động tạo URL:
    # POST /auth/register/
    path('', include(router.urls)),
    
    # URL lấy thông tin cá nhân:
        # URL xem thông tin: GET /auth/me/

    path('me/', UserProfileView.as_view(), name='user-profile'),

    # URL đăng nhập: POST /auth/login/
    path('login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    
    # URL làm mới token: POST /auth/refresh/
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('activate/<str:uidb64>/<str:token>/', ActivateAccountView.as_view(), name='activate-account'),

    path('resend-activation/', ResendActivationEmailView.as_view(), name='resend-activation'),
]