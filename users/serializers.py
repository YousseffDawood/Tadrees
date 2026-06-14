from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Staff, Admin, Teacher, Student,User


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        attrs = super().validate(attrs)
        user = self.user
        profile = getattr(user, 'staff', None) or getattr(user, 'admin', None)
        attrs['role'] = user.role.lower()
        attrs['name'] = profile.name if profile else ''
        attrs['user_id'] = user.id
        return attrs


class StaffCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    name = serializers.CharField(write_only=True)
    phone = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "name",
            "phone",
            "password",
            "confirm_password",
        ]

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError("Passwords do not match")
        return attrs

    def create(self, validated_data):
        name = validated_data.pop("name")
        phone = validated_data.pop("phone")
        validated_data.pop("confirm_password")
        password = validated_data.pop("password")

        user = User.objects.create_user(
            role=User.Roles.STAFF,
            password=password,
            **validated_data
        )

        Staff.objects.create(user=user, name=name, phone=phone)

        return user

class StaffListSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    email = serializers.EmailField(source='user.email')

    class Meta:
        model = Staff
        fields = ['id', 'name', 'phone', 'email', 'username', 'title']


class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = '__all__'


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'
