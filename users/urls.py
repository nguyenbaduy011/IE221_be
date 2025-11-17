# users/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AdminUserViewSet

router = DefaultRouter()
# Để rỗng r'' vì bên ngoài đã định nghĩa prefix 'users/' rồi
router.register(r'', AdminUserViewSet, basename='admin-users') 

urlpatterns = [
    path('', include(router.urls)),
]