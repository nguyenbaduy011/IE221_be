# users/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet

router = DefaultRouter()
# Để rỗng r'' vì bên ngoài đã định nghĩa prefix 'users/' rồi
router.register(r'', UserViewSet, basename='admin-users') 

urlpatterns = [
    path('', include(router.urls)),
]