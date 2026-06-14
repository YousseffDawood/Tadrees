from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
from .models import Subject, Schedule, SpecialSchedule, Room, Enrollment


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = '__all__'
        depth = 1


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = '__all__'


class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = '__all__'
        read_only_fields = ['day']

    def create(self, validated_data):
        try:
            return super().create(validated_data)
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.message_dict)

    def update(self, instance, validated_data):
        try:
            return super().update(instance, validated_data)
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.message_dict)


class SpecialScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecialSchedule
        fields = '__all__'

    def create(self, validated_data):
        try:
            return super().create(validated_data)
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.message_dict)

    def update(self, instance, validated_data):
        try:
            return super().update(instance, validated_data)
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.message_dict)


class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = '__all__'
