from django.urls import path, include
from courses.views.supervisor_views import *
from courses.views.trainee_views import *
from courses.views.admin_views import *

urlpatterns = [

    path(
        "admin/courses/",
        AdminCourseListView.as_view(),
        name="admin-course-list"
    ),

    path(
        "supervisor/courses/create/",
        SupervisorCourseCreateView.as_view(),
        name="supervisor-course-create"
    ),
    path(
        "supervisor/stats/",
        SupervisorDashboardStatsView.as_view(),
        name="supervisor-stats"
    ),
    path(
        "supervisor/courses/my-courses/",
        SupervisorMyCourseListView.as_view(),
        name="supervisor-my-course-list"
    ),
    path(
        "supervisor/courses/",
        SupervisorCourseListView.as_view(),
        name="supervisor-course-list"
    ),
    path(
        "supervisor/courses/<int:pk>/",
        SupervisorCourseDetailView.as_view(),
        name="supervisor-course-detail"
    ),


    path(
        "trainee/courses/",
        TraineeMyCoursesView.as_view(),
        name="trainee-my-courses"
    ),
    path(
        "trainee/courses/<int:course_id>/detail/",
        TraineeCourseDetailView.as_view(),
        name="trainee-course-subjects"
    ),


    path(
        "<int:course_id>/members",
        CourseMembersView.as_view(),
        name="trainee-course-detail"
    ),
    path(
        "supervisor/courses/<int:course_id>/students/",
        SupervisorCourseStudentsView.as_view(),
        name="supervisor-course-students"
    ),
    path(
        "supervisor/subjects/<int:subject_id>/student/<int:student_id>/",
        SupervisorUserSubjectDetailView.as_view(),
        name="supervisor-user-subject-detail"
    ),
    path(
        "supervisor/subjects/<int:subject_id>/tasks/",
        SupervisorSubjectTaskCreateView.as_view(),
        name="supervisor-subject-task-create"
    ),

    path(
        "supervisor/user-subjects/<int:pk>/assessment/",
        SupervisorUserSubjectAssessmentView.as_view(),
        name="supervisor-user-subject-assessment"
    ),

    path(
        "supervisor/tasks/<int:pk>/",
        SupervisorTaskToggleView.as_view(),
        name="supervisor-task-toggle"
    ),

    path(
        "supervisor/user-subjects/<int:pk>/complete/",
        SupervisorUserSubjectCompleteView.as_view(),
        name="supervisor-user-subject-complete"
    ),
]
