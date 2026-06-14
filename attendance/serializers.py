from rest_framework import serializers
from .models import Session
from users.models import Student


class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = '__all__'


class StudentMinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['id', 'name', 'phone']


class TodaySessionSerializer(serializers.ModelSerializer):
    students_attended = StudentMinSerializer(many=True, read_only=True)
    subject = serializers.SerializerMethodField()
    teacher = serializers.SerializerMethodField()
    time_start = serializers.SerializerMethodField()
    special_schedule = serializers.SerializerMethodField()

    class Meta:
        model = Session
        fields = ['id', 'session_date', 'subject', 'teacher', 'time_start',
                  'cancelled', 'special_schedule', 'notes', 'students_attended']

    def get_subject(self, obj):
        return obj.subject.name if obj.subject else None

    def get_teacher(self, obj):
        return obj.teacher.name if obj.teacher else None

    def get_time_start(self, obj):
        source = obj.source
        if source and source.time_start:
            return source.time_start.isoformat()
        return None

    def get_special_schedule(self, obj):
        return obj.special_schedule_id is not None


class SessionHistorySerializer(serializers.ModelSerializer):
    students_attended = StudentMinSerializer(many=True, read_only=True)
    subject = serializers.CharField(source='subject.name', read_only=True)
    teacher = serializers.CharField(source='teacher.name', read_only=True)
    room = serializers.CharField(source='room.name', read_only=True)

    class Meta:
        model = Session
        fields = ['id', 'session_date', 'subject', 'teacher', 'room',
                  'cancelled', 'notes', 'students_attended']


class UpcomingSessionSerializer(serializers.ModelSerializer):
    subject_name = serializers.SerializerMethodField()
    teacher_name = serializers.SerializerMethodField()
    room_name = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    time_start = serializers.SerializerMethodField()
    time_end = serializers.SerializerMethodField()

    class Meta:
        model = Session
        fields = ['id', 'session_date', 'subject_name', 'teacher_name',
                  'room_name', 'price', 'time_start', 'time_end', 'cancelled']

    def get_subject_name(self, obj):
        return obj.subject.name if obj.subject else ''

    def get_teacher_name(self, obj):
        return obj.teacher.name if obj.teacher else ''

    def get_room_name(self, obj):
        return obj.room.name if obj.room else ''

    def get_price(self, obj):
        return float(obj.price) if obj.price else 0

    def get_time_start(self, obj):
        source = obj.source
        if source and source.time_start:
            return source.time_start.isoformat()
        return None

    def get_time_end(self, obj):
        source = obj.source
        if source and hasattr(source, 'time_end'):
            return source.time_end.isoformat()
        return None


class AttendSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=20)

    def validate_phone_number(self, value):
        from users.models import Student
        try:
            self.student = Student.objects.get(phone=value)
        except Student.DoesNotExist:
            raise serializers.ValidationError('No student found with this phone number')
        return value
