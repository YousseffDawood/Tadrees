from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('subjects', views.SubjectViewSet)
router.register('schedules', views.ScheduleViewSet)
router.register('special-schedules', views.SpecialScheduleViewSet)
router.register('rooms', views.RoomViewSet)
router.register('enrollments', views.EnrollmentViewSet)

urlpatterns = [
    path('teachers/<int:pk>/subject/', views.TeacherSubjectsView.as_view(), name='teacher-subjects'),
    path('teachers/<int:pk>/schedule/', views.TeacherScheduleView.as_view(), name='teacher-schedule'),
    path('', include(router.urls)),
]
