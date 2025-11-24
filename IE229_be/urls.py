from rest_framework.routers import DefaultRouter, SimpleRouter # Import SimpleRouter
from users.views import CommentViewSet, UserViewSet # Thêm UserViewSet vào đây
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from users.views import CommentViewSet
from daily_reports.views.trainee_views import TraineeDailyReportViewSet
from daily_reports.views.supervisor_views import SupervisorDailyReportViewSet
from daily_reports.views.admin_views import AdminDailyReportViewSet

router = DefaultRouter()
router.register(r'trainee/daily_reports', TraineeDailyReportViewSet, basename='trainee-daily-report')
router.register(r'supervisor/daily_reports', SupervisorDailyReportViewSet, basename='supervisor-daily-report')
router.register(r'admin/daily_reports', AdminDailyReportViewSet, basename='admin-daily-report')


router_resources = DefaultRouter()
router_resources.register(r'comments', CommentViewSet, basename='comments')
# --- Router RIÊNG cho Admin User ---
# Chỉ chứa UserViewSet
admin_user_router = SimpleRouter()
admin_user_router.register(r'', UserViewSet, basename='admin-users')

urlpatterns = [
    path('django-admin/', admin.site.urls),

    path('auth/', include('authen.urls')),

    path('api/', include([
        path('', include(router.urls)),
        
        # 1. PATH TRAINEE (Dùng users/urls.py đã được lược bỏ UserViewSet)
        path('users/', include('users.urls')), 
        
        # 2. PATH ADMIN (Chỉ include UserViewSet)
        path('admin/', include([
            # Thay thế include('users.urls') bằng admin_user_router
            path('users/', include(admin_user_router.urls)), 
        ])),
        
        path('', include('courses.urls')),
        path('', include('subjects.urls')),
        path('daily_reports/', include('daily_reports.urls')),

        path('resources/', include(router_resources.urls)),

    ])),
]