from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.trainee_views import TraineeDailyReportViewSet
from .views.supervisor_views import SupervisorDailyReportViewSet
from .views.admin_views import AdminDailyReportViewSet

router = DefaultRouter()
router.register(r'trainee/daily_reports', TraineeDailyReportViewSet, basename='trainee-daily-report')
router.register(r'supervisor/daily_reports', SupervisorDailyReportViewSet, basename='supervisor-daily-report')
router.register(r'admin/daily_reports', AdminDailyReportViewSet, basename='admin-daily-report')

urlpatterns = [
    path('api/', include(router.urls)),
]
