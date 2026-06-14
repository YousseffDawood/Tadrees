from rest_framework import serializers
from .models import CenterInfo, Announcement


class CenterInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CenterInfo
        fields = '__all__'


class AnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = '__all__'
        read_only_fields = ['announcer']
