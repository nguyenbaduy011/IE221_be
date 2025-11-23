# users/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TraineeMySubjectsView, 
    TraineeSubjectActionViewSet, 
    UserTaskViewSet, 
    UserViewSet
)

router = DefaultRouter()

# 1. Quản lý User (Admin dùng) -> api/users/
router.register(r'', UserViewSet, basename='users') 

# 2. Nộp bài/Update Task (Trainee dùng) -> api/users/user-tasks/
router.register(r'user-tasks', UserTaskViewSet, basename='user-tasks') 

# 3. Actions với môn học (Trainee dùng) -> api/users/my-course-subjects/
router.register(r'my-course-subjects', TraineeSubjectActionViewSet, basename='my-course-subjects')

urlpatterns = [
    # Đặt các path cụ thể (custom view) lên TRƯỚC router để tránh bị conflict với ID
    path('my-subjects/', TraineeMySubjectsView.as_view(), name='trainee-my-subjects'),
    
    # Include router
    path('', include(router.urls)),
]