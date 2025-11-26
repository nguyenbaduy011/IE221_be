from django.urls import path, include
from courses.views.supervisor_views import *
from courses.views.trainee_views import *
from courses.views.admin_views import *
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"courses", CourseManagementViewSet, basename="course-management")

urlpatterns = [
    path("", include(router.urls)),
    path("admin/courses/", AdminCourseListView.as_view(), name="admin-course-list"),
    path(
        "supervisor/courses/create/",
        SupervisorCourseCreateView.as_view(),
        name="supervisor-course-create",
    ),
    path(
        "admin/courses/create/",
        SupervisorCourseCreateView.as_view(),
        name="admin-course-create",
    ),
    path(
        "supervisor/stats/",
        SupervisorDashboardStatsView.as_view(),
        name="supervisor-stats",
    ),
    path(
        "admin/stats/",
        AdminDashboardStatsView.as_view(),
        name="admin-stats",
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
        "supervisor/courses/<int:course_id>/",
        SupervisorCourseDetailView.as_view(),
        name="supervisor-course-detail",
    ),
    path(
        "admin/courses/<int:course_id>/",
        AdminCourseDetailView.as_view(),
        name="admin-course-detail",
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
    path(
        "supervisor/courses/<int:course_id>/students/",
        SupervisorCourseStudentsView.as_view(),
        name="supervisor-course-students",
    ),
    path(
        "supervisor/subjects/<int:subject_id>/student/<int:student_id>/",
        SupervisorUserSubjectDetailView.as_view(),
        name="supervisor-user-subject-detail",
    ),
    path(
        "supervisor/subjects/<int:subject_id>/tasks/",
        SupervisorSubjectTaskCreateView.as_view(),
        name="supervisor-subject-task-create",
    ),
    path(
        "supervisor/user-subjects/<int:pk>/assessment/",
        SupervisorUserSubjectAssessmentView.as_view(),
        name="supervisor-user-subject-assessment",
    ),
    path(
        "supervisor/tasks/<int:pk>/",
        SupervisorTaskToggleView.as_view(),
        name="supervisor-task-toggle",
    ),
    path(
        "supervisor/user-subjects/<int:pk>/complete/",
        SupervisorUserSubjectCompleteView.as_view(),
        name="supervisor-user-subject-complete",
    ),
    path(
        "admin/courses/<int:pk>/trainees/",
        CourseManagementViewSet.as_view({"get": "get_trainees"}),
        name="admin-course-trainees",
    ),
    path(
        "supervisor/courses/<int:pk>/trainees/",
        CourseManagementViewSet.as_view({"get": "get_trainees"}),
        name="supervisor-course-trainees",
    ),
    path(
        "admin/courses/<int:pk>/subjects/",
        CourseManagementViewSet.as_view({"get": "get_subjects"}),
        name="admin-course-subjects",
    ),
    path(
        "admin/courses/<int:pk>/reorder-subjects/",
        CourseManagementViewSet.as_view({"post": "reorder_subjects"}),
    ),
    path(
        "admin/course-subjects/<int:pk>/",
        CourseSubjectUpdateView.as_view(),
        name="admin-course-subject-update",
    ),
    path(
        "supervisor/course-subjects/<int:pk>/",
        CourseSubjectUpdateView.as_view(),
        name="supervisor-course-subject-update",
    ),
    path(
        "admin/courses/<int:pk>/add-task/",
        CourseManagementViewSet.as_view({"post": "add_task"}),
        name="admin-course-add-task",
    ),
    path(
        "admin/tasks/<int:pk>/detail/",
        SupervisorTaskDetailView.as_view(),
        name="admin-task-detail",
    ),
    path(
        "supervisor/courses/<int:pk>/subjects/",
        CourseManagementViewSet.as_view({"get": "get_subjects"}),
        name="supervisor-course-subjects",
    ),
    path(
        "supervisor/courses/<int:pk>/reorder-subjects/",
        CourseManagementViewSet.as_view({"post": "reorder_subjects"}),
        name="supervisor-course-reorder-subjects",
    ),
    path(
        "supervisor/courses/<int:pk>/add-task/",
        CourseManagementViewSet.as_view({"post": "add_task"}),
        name="supervisor-course-add-task",
    ),
]
