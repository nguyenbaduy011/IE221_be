from django.urls import path, include
from courses.views.supervisor_views import *
from courses.views.trainee_views import *
from courses.views.admin_views import *

urlpatterns = [
    path('admin/courses/', AdminCourseListView.as_view(), name='admin-course-list'),

    path('supervisor/courses/create/', SupervisorCourseCreateView.as_view(), name='supervisor-course-create'),
    path('supervisor/stats/', SupervisorDashboardStatsView.as_view(), name='supervisor-stats'),
    path('supervisor/courses/my-courses/', SupervisorMyCourseListView.as_view(), name='supervisor-my-course-list'),

    path('supervisor/courses/<int:pk>/', SupervisorCourseDetailView.as_view(), name='supervisor-course-detail'),

    path('trainee/courses/', TraineeMyCoursesView.as_view(), name='trainee-my-courses'),
    path('trainee/courses/<int:course_id>/detail/', TraineeCourseDetailView.as_view(), name='trainee-course-subjects'),
    
    path('<int:course_id>/members', CourseMembersView.as_view(), name='trainee-course-detail'), 
]