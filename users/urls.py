from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TraineeMySubjectsView,
    TraineeSubjectActionViewSet,
    UserTaskViewSet,
    UserViewSet
)

router = DefaultRouter()

router.register(r'', UserViewSet, basename='users')

router.register(r'user-tasks', UserTaskViewSet, basename='user-tasks')

router.register(r'my-course-subjects', TraineeSubjectActionViewSet, basename='my-course-subjects')

urlpatterns = [
    path('my-subjects/', TraineeMySubjectsView.as_view(), name='trainee-my-subjects'),
    path('', include(router.urls)),
]
