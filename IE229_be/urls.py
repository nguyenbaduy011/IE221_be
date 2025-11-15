from django.contrib import admin
from django.urls import path, include  
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
) 

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # URL của app 'authen' (ví dụ: /auth/register, /auth/me)
    path('auth/', include('authen.urls')),
    
    # URLs để Next.js lấy và làm mới token
    
    
    # URLs của các app khác
    path('courses/', include('courses.urls')),
    path('daily_reports/', include('daily_reports.urls')),
]