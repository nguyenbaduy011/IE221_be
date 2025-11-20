from django.urls import path, include
from rest_framework.routers import DefaultRouter

from subjects.views.supervisor_views import (
    SupervisorSubjectListView, 
    SupervisorSubjectDetailView,
    TaskViewSet  # Class này giờ xử lý cho cả Admin, Supervisor và Trainee
)
from subjects.views.trainee_views import TraineeSubjectListView, TraineeSubjectDetailView

# --- Router ---
# Vì TaskViewSet dùng chung cho cả Trainee (Read) và Supervisor (Write)
# nên ta đặt nó ở router chung, không gắn prefix 'supervisor' nữa.
router = DefaultRouter()
router.register(r'tasks', TaskViewSet, basename='task') 
# => Tạo ra các url: /tasks/, /tasks/{id}/

urlpatterns = [
    # --- Include Router URLs ---
    # Đặt ở đầu để khớp với các route của ViewSet (tasks/)
    path('', include(router.urls)),


    # --- Supervisor Namespace (Các APIView thủ công) ---
    path(
        'supervisor/subjects/', 
        SupervisorSubjectListView.as_view(), 
        name='supervisor-subject-list'
    ),
    path(
        'supervisor/subjects/<int:subject_id>/', 
        SupervisorSubjectDetailView.as_view(), 
        name='supervisor-subject-detail'
    ),

    # --- Trainee Namespace ---
    path(
        'trainee/subjects/', 
        TraineeSubjectListView.as_view(), 
        name='trainee-subject-list'
    ),
    path(
        'trainee/subjects/<int:subject_id>/', 
        TraineeSubjectDetailView.as_view(), 
        name='trainee-subject-detail'
    ),
]