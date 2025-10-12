from django.urls import path
from .views import *

urlpatterns = [
    path('courses/', CourseListView.as_view(), name='course-list'), # Đường dẫn để lấy danh sách khóa học
    path('courses/detail/', CourseDetailView.as_view(), name='course-detail'), # Đường dẫn để lấy chi tiết khóa học theo ID
]