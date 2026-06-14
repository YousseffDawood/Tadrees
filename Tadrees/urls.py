from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('users.urls')),
    path('api/academics/', include('academics.urls')),
    path('api/attendance/', include('attendance.urls')),
    path('api/finance/', include('finance.urls')),
    path('api/center/', include('center.urls')),
]
