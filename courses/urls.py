from django.urls import path, include
from courses.views.supervisor_views import *
from courses.views.trainee_views import *
from courses.views.admin_views import *

urlpatterns = [
    path("admin/courses/", AdminCourseListView.as_view(), name="admin-course-list"),
    path(
        "supervisor/courses/create/",
        SupervisorCourseCreateView.as_view(),
        name="supervisor-course-create",
    ),
    path(
        "supervisor/stats/",
        SupervisorDashboardStatsView.as_view(),
        name="supervisor-stats",
    ),
    path(
        "supervisor/courses/my-courses/",
        SupervisorMyCourseListView.as_view(),
        name="supervisor-my-course-list",
    ),
    path(
        "supervisor/courses/",
        SupervisorCourseListView.as_view(),
        name="supervisor-course-list",
    ),
    path(
        "supervisor/courses/<int:pk>/",
        SupervisorCourseDetailView.as_view(),
        name="supervisor-course-detail",
    ),
    path("trainee/courses/", TraineeMyCoursesView.as_view(), name="trainee-my-courses"),
    path(
        "trainee/courses/<int:course_id>/detail/",
        TraineeCourseDetailView.as_view(),
        name="trainee-course-subjects",
    ),
    path(
        "<int:course_id>/members",
        CourseMembersView.as_view(),
        name="trainee-course-detail",
    ),
    path(
        "admin/courses/<int:pk>/update/",
        CourseManagementViewSet.as_view({"put": "update", "patch": "partial_update"}),
        name="admin-course-update",
    ),
    path(
        "admin/courses/<int:pk>/delete/",
        CourseManagementViewSet.as_view({"delete": "destroy"}),
        name="admin-course-delete",
    ),
    path(
        "admin/courses/<int:pk>/add-supervisors/",
        CourseManagementViewSet.as_view({"post": "add_supervisors"}),
        name="admin-course-add-supervisors",
    ),
    path(
        "admin/courses/<int:pk>/remove-supervisor/",
        CourseManagementViewSet.as_view({"delete": "remove_supervisor"}),
        name="admin-course-remove-supervisor",
    ),
    path(
        "admin/courses/<int:course_id>/add-trainees/",
        CourseManagementViewSet.as_view({"post": "add_trainees"}),
        name="admin-course-add-trainees",
    ),
    path(
        "admin/courses/<int:pk>/remove-trainee/",
        CourseManagementViewSet.as_view({"delete": "remove_trainee"}),
        name="admin-course-remove-trainee",
    ),
    path(
        "admin/courses/<int:pk>/add-subject/",
        CourseManagementViewSet.as_view({"post": "add_subject"}),
        name="admin-course-add-subject",
    ),
    path(
        "admin/courses/<int:pk>/remove-subject/",
        CourseManagementViewSet.as_view({"delete": "remove_subject"}),
        name="admin-course-remove-subject",
    ),
    path(
        "supervisor/courses/<int:pk>/update/",
        CourseManagementViewSet.as_view({"put": "update", "patch": "partial_update"}),
        name="supervisor-course-update",
    ),
    path(
        "supervisor/courses/<int:pk>/delete/",
        CourseManagementViewSet.as_view({"delete": "destroy"}),
        name="supervisor-course-delete",
    ),
    path(
        "supervisor/courses/<int:pk>/add-supervisors/",
        CourseManagementViewSet.as_view({"post": "add_supervisors"}),
        name="supervisor-course-add-supervisors",
    ),
    path(
        "supervisor/courses/<int:pk>/remove-supervisor/",
        CourseManagementViewSet.as_view({"delete": "remove_supervisor"}),
        name="supervisor-course-remove-supervisor",
    ),
    # Lưu ý: method add_trainees của bạn dùng tham số course_id, nên URL phải dùng <int:course_id>
    path(
        "supervisor/courses/<int:course_id>/add-trainees/",
        CourseManagementViewSet.as_view({"post": "add_trainees"}),
        name="supervisor-course-add-trainees",
    ),
    path(
        "supervisor/courses/<int:pk>/remove-trainee/",
        CourseManagementViewSet.as_view({"delete": "remove_trainee"}),
        name="supervisor-course-remove-trainee",
    ),
    path(
        "supervisor/courses/<int:pk>/add-subject/",
        CourseManagementViewSet.as_view({"post": "add_subject"}),
        name="supervisor-course-add-subject",
    ),
    path(
        "supervisor/courses/<int:pk>/remove-subject/",
        CourseManagementViewSet.as_view({"delete": "remove_subject"}),
        name="supervisor-course-remove-subject",
    ),
]
