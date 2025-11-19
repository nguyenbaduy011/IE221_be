from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from daily_reports.views.trainee_views import TraineeDailyReportViewSet
from daily_reports.views.supervisor_views import SupervisorDailyReportViewSet
from daily_reports.views.admin_views import AdminDailyReportViewSet

router = DefaultRouter()
router.register(r'trainee/daily_reports', TraineeDailyReportViewSet, basename='trainee-daily-report')
router.register(r'supervisor/daily_reports', SupervisorDailyReportViewSet, basename='supervisor-daily-report')
router.register(r'admin/daily_reports', AdminDailyReportViewSet, basename='admin-daily-report')

urlpatterns = [
    path('django-admin/', admin.site.urls),

    path('auth/', include('authen.urls')),

    path('api/', include([
        path('', include(router.urls)),
        path('admin/', include([
            path('users/', include('users.urls')),
        ])),
        path('courses/', include('courses.urls')),
        path('', include('subjects.urls')),
        path('daily_reports/', include('daily_reports.urls')),
    ])),
]
