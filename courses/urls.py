from django.urls import path, include
from courses.views.supervisor_views import SupervisorCourseListView, SupervisorCourseDetailView
from courses.views.trainee_views import TraineeCourseDetailView

urlpatterns = [
    path('api/supervisor/courses/', SupervisorCourseListView.as_view(), name='supervisor-course-list'),
    path('api/supervisor/courses/<int:pk>/', SupervisorCourseDetailView.as_view(), name='supervisor-course-detail'),
    path('api/trainee/courses/<int:pk>/', TraineeCourseDetailView.as_view(), name='trainee-course-detail'),
]