from datetime import date, timedelta
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from users.permissions import has_role
from academics.models import Enrollment
from .models import Session
from .serializers import (TodaySessionSerializer, AttendSerializer,
                          SessionHistorySerializer, UpcomingSessionSerializer)


class TodaySessionsView(generics.ListAPIView):
    queryset = Session.objects.all()
    serializer_class = TodaySessionSerializer
    permission_classes = [IsAuthenticated, has_role('staff', 'admin')]

    def get_queryset(self):
        return Session.objects.filter(session_date=date.today())


class AttendView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated, has_role('staff', 'admin')]

    def post(self, request, pk):
        serializer = AttendSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        student = serializer.student

        try:
            session = Session.objects.get(pk=pk)
        except Session.DoesNotExist:
            return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)

        subject = None
        if session.schedule:
            subject = session.schedule.subject
        elif session.special_schedule:
            subject = session.special_schedule.subject

        if not subject:
            return Response({'error': 'Session has no subject'}, status=status.HTTP_400_BAD_REQUEST)

        enrolled = Enrollment.objects.filter(
            student=student, subject=subject, paid=True
        ).exists()

        if not enrolled:
            return Response(
                {'error': 'Student is not enrolled or has not paid for this subject'},
                status=status.HTTP_403_FORBIDDEN
            )

        session.students_attended.add(student)
        return Response({'status': 'attended'}, status=status.HTTP_200_OK)


class UpcomingSessionsView(generics.ListAPIView):
    serializer_class = UpcomingSessionSerializer
    permission_classes = [IsAuthenticated, has_role('staff', 'admin')]

    def get_queryset(self):
        today = date.today()
        end = today + timedelta(days=7)
        return Session.objects.filter(
            session_date__gte=today, session_date__lte=end,
            cancelled=False
        ).order_by('session_date')


class AttendanceHistoryView(generics.ListAPIView):
    serializer_class = SessionHistorySerializer
    permission_classes = [IsAuthenticated, has_role('staff', 'admin')]

    def get_queryset(self):
        return Session.objects.filter(
            session_date__lt=date.today()
        ).order_by('-session_date')
