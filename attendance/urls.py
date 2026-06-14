from django.urls import path
from . import views

urlpatterns = [
    path('sessions/today/', views.TodaySessionsView.as_view(), name='sessions-today'),
    path('sessions/upcoming/', views.UpcomingSessionsView.as_view(), name='sessions-upcoming'),
    path('sessions/history/', views.AttendanceHistoryView.as_view(), name='attendance-history'),
    path('sessions/<int:pk>/attend/', views.AttendView.as_view(), name='session-attend'),
]
