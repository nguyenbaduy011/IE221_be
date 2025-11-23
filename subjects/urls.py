from django.urls import path, include
from rest_framework.routers import DefaultRouter

from subjects.views.supervisor_views import (
    SupervisorSubjectListView, 
    SupervisorSubjectDetailView,
    TaskViewSet,
    SupervisorCategoryViewSet
)
from subjects.views.trainee_views import TraineeSubjectListView, TraineeSubjectDetailView

# --- Shared Router ---
# TaskViewSet dùng chung, URL dạng: /tasks/
router = DefaultRouter()
router.register(r'tasks', TaskViewSet, basename='task') 

# --- Supervisor Specific Router ---
supervisor_router = DefaultRouter()
supervisor_router.register(r'categories', SupervisorCategoryViewSet, basename='supervisor-category')
# URL sẽ là: /supervisor/categories/

urlpatterns = [
    # --- Include Shared Router URLs ---
    path('', include(router.urls)),

    # --- Include Supervisor Router URLs ---
    path('supervisor/', include(supervisor_router.urls)),

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