from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegistrationViewSet, UserProfileView, ActivateAccountView, ResendActivationEmailView, MyTokenObtainPairView, LogoutView, ChangePasswordView

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


router = DefaultRouter()
router.register(r'register', RegistrationViewSet, basename='register')


urlpatterns = [
    path('', include(router.urls)),

    path('me/', UserProfileView.as_view(), name='user-profile'),

    path('login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('activate/<str:uidb64>/<str:token>/', ActivateAccountView.as_view(), name='activate-account'),

    path('resend-activation/', ResendActivationEmailView.as_view(), name='resend-activation'),

    path('logout/', LogoutView.as_view(), name='logout'),

    path('change-password/', ChangePasswordView.as_view(), name='change-password'),


]