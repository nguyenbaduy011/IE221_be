from django.urls import path, include
from courses.views.supervisor_views import *
from courses.views.trainee_views import *

urlpatterns = [
    path('supervisor/courses/', SupervisorCourseListView.as_view(), name='supervisor-course-list'),
    path('supervisor/courses/<int:pk>/', SupervisorCourseDetailView.as_view(), name='supervisor-course-detail'),
    path('trainee/courses/<int:pk>/', TraineeCourseDetailView.as_view(), name='trainee-course-detail'),
    path('supervisor/courses/create/', SupervisorCourseCreateView.as_view(), name='supervisor-course-create'),
]