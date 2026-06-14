from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('students', views.StudentViewSet)

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('token/refresh/', views.TokenRefreshViewCustom.as_view(), name='token-refresh'),
    path('staff/', views.StaffCreateView.as_view(), name='staff-create'),
    path('staff/list/', views.StaffListView.as_view(), name='staff-list'),
    path('teachers/', views.TeacherListCreateView.as_view(), name='teacher-list-create'),
    path('teachers/<int:pk>/', views.TeacherDeleteView.as_view(), name='teacher-delete'),
    path('admin/dashboard/', views.AdminDashboardView.as_view(), name='admin-dashboard'),
    path('', include(router.urls)),
]
