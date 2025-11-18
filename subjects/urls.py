from django.urls import path
from subjects.views.supervisor_views import SupervisorSubjectListView, SupervisorSubjectDetailView
from subjects.views.trainee_views import TraineeSubjectListView, TraineeSubjectDetailView

urlpatterns = [
    # --- Supervisor Namespace ---
    # Tương ứng: namespace :supervisor { resources :subjects }
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
    # Tương ứng: namespace :trainee { resources :subjects, only: [:index, :show] }
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