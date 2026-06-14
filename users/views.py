from rest_framework import generics, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .models import Staff, Teacher, Student
from .serializers import (
    MyTokenObtainPairSerializer, StaffCreateSerializer,
    StaffListSerializer, TeacherSerializer, StudentSerializer
)
from .permissions import has_role, IsAdmin


class LoginView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
    permission_classes = [AllowAny]


class TokenRefreshViewCustom(TokenRefreshView):
    permission_classes = [AllowAny]


class StaffCreateView(generics.CreateAPIView):
    queryset = Staff.objects.all()
    serializer_class = StaffCreateSerializer
    permission_classes = [IsAuthenticated, IsAdmin]


class TeacherListCreateView(generics.ListCreateAPIView):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer
    permission_classes = [IsAuthenticated, has_role('staff', 'admin')]


class TeacherDeleteView(generics.DestroyAPIView):
    queryset = Teacher.objects.all()
    permission_classes = [IsAuthenticated, IsAdmin]


class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated, has_role('staff', 'admin')]


class StaffListView(generics.ListAPIView):
    queryset = Staff.objects.select_related('user').all()
    serializer_class = StaffListSerializer
    permission_classes = [IsAuthenticated, IsAdmin]


class AdminDashboardView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        staff = StaffListSerializer(Staff.objects.select_related('user').all(), many=True).data
        teachers = TeacherSerializer(Teacher.objects.all(), many=True).data
        return Response({'staff': staff, 'teachers': teachers})
