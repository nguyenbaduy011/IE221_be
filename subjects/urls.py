from django.urls import path, include
from rest_framework.routers import DefaultRouter

from subjects.views.supervisor_views import (
    SupervisorSubjectListView, 
    SupervisorSubjectDetailView,
    SupervisorTaskViewSet
)
from subjects.views.trainee_views import TraineeSubjectListView, TraineeSubjectDetailView

# Tạo router cho các ViewSet của Supervisor
supervisor_router = DefaultRouter()
# Đăng ký 'tasks' -> sẽ tạo ra các url: /supervisor/tasks/, /supervisor/tasks/{id}/
supervisor_router.register(r'tasks', SupervisorTaskViewSet, basename='supervisor-task')

urlpatterns = [
    # --- Supervisor Namespace ---
    
    # 1. Subjects (APIView truyền thống)
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

    # 2. Tasks (Sử dụng Router)
    # Include router urls vào path 'supervisor/'
    path('supervisor/', include(supervisor_router.urls)),


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