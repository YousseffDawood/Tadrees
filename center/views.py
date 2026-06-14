from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from users.permissions import has_role
from .models import CenterInfo, Announcement
from .serializers import CenterInfoSerializer, AnnouncementSerializer


class CenterInfoViewSet(viewsets.ModelViewSet):
    queryset = CenterInfo.objects.all()
    serializer_class = CenterInfoSerializer
    permission_classes = [IsAuthenticated, has_role('staff', 'admin')]


class AnnouncementViewSet(viewsets.ModelViewSet):
    queryset = Announcement.objects.all()
    serializer_class = AnnouncementSerializer
    permission_classes = [IsAuthenticated, has_role('staff', 'admin')]

    def perform_create(self, serializer):
        serializer.save(announcer=self.request.user)
