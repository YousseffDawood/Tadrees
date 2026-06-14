from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated
from users.permissions import has_role
from .models import Subject, Schedule, SpecialSchedule, Room, Enrollment
from .serializers import (
    SubjectSerializer, ScheduleSerializer,
    SpecialScheduleSerializer, RoomSerializer, EnrollmentSerializer
)


class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [IsAuthenticated, has_role('staff', 'admin')]


class ScheduleViewSet(viewsets.ModelViewSet):
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer
    permission_classes = [IsAuthenticated, has_role('staff', 'admin')]


class SpecialScheduleViewSet(viewsets.ModelViewSet):
    queryset = SpecialSchedule.objects.all()
    serializer_class = SpecialScheduleSerializer
    permission_classes = [IsAuthenticated, has_role('staff', 'admin')]


class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [IsAuthenticated, has_role('staff', 'admin')]


class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated, has_role('staff', 'admin')]


class TeacherSubjectsView(generics.ListAPIView):
    serializer_class = SubjectSerializer
    permission_classes = [IsAuthenticated, has_role('staff', 'admin')]

    def get_queryset(self):
        return Subject.objects.filter(teacher__id=self.kwargs['pk'])


class TeacherScheduleView(generics.ListAPIView):
    serializer_class = ScheduleSerializer
    permission_classes = [IsAuthenticated, has_role('staff', 'admin')]

    def get_queryset(self):
        return Schedule.objects.filter(teacher__id=self.kwargs['pk'])
