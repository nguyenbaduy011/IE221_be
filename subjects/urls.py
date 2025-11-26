from django.urls import path, include
from rest_framework.routers import DefaultRouter

from subjects.views.supervisor_views import (
    SupervisorSubjectListView,
    SupervisorSubjectDetailView,
    TaskViewSet,
    SupervisorCategoryViewSet,
    SubjectListView,
)
from subjects.views.trainee_views import (
    TraineeSubjectListView,
    TraineeSubjectDetailView,
)

router = DefaultRouter()
router.register(r"tasks", TaskViewSet, basename="task")

supervisor_router = DefaultRouter()
supervisor_router.register(
    r"categories", SupervisorCategoryViewSet, basename="supervisor-category"
)
admin_router = DefaultRouter()
admin_router.register(
    r"categories", SupervisorCategoryViewSet, basename="admin-category"
)

urlpatterns = [
    path("", include(router.urls)),
    path("supervisor/", include(supervisor_router.urls)),
    path(
        "supervisor/subjects/",
        SupervisorSubjectListView.as_view(),
        name="supervisor-subject-list",
    ),
    path(
        "supervisor/subjects/<int:subject_id>/",
        SupervisorSubjectDetailView.as_view(),
        name="supervisor-subject-detail",
    ),
    path(
        "supervisor/subjects/",
        SubjectListView.as_view(),
        name="supervisor-subject-list",
    ),
    path(
        "trainee/subjects/",
        TraineeSubjectListView.as_view(),
        name="trainee-subject-list",
    ),
    path(
        "trainee/subjects/<int:subject_id>/",
        TraineeSubjectDetailView.as_view(),
        name="trainee-subject-detail",
    ),
    path("admin/", include(admin_router.urls)),
    path("admin/subjects/", SubjectListView.as_view(), name="admin-subject-list"),
]
