# IE229_be/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # 1. Django Admin Panel (Giao diện quản trị có sẵn của Django)
    # Mình đổi thành 'django-admin/' để tránh nhầm lẫn với API admin của bạn
    path('django-admin/', admin.site.urls),

    # 2. Authentication (Theo yêu cầu: /auth/login, /auth/register...)
    path('auth/', include('authen.urls')),

    # 3. API Group (Bắt đầu bằng /api/)
    path('api/', include([
        
        # --- Nhóm Admin API (/api/admin/...) ---
        path('admin/', include([
            # Trỏ vào app 'users' chúng ta vừa tách
            # URL kết quả: /api/admin/users/
            path('users/', include('users.urls')), 
            
            # Sau này có thống kê, báo cáo thì thêm vào đây
            # path('stats/', include('stats.urls')),
        ])),

        # --- Nhóm Public/User API (/api/...) ---
        # URL kết quả: /api/courses/
        path('courses/', include('courses.urls')),

        # URL kết quả: /api/subjects/
        path('', include('subjects.urls')),
        
        # URL kết quả: /api/daily_reports/
        path('daily_reports/', include('daily_reports.urls')),
    ])),
]