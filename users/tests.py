from django.test import TestCase
from django.contrib.auth.hashers import make_password
from rest_framework.test import APIClient
from rest_framework import status
from .models import Staff, Admin, Student, Teacher, User


class UsersAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        admin_user = User.objects.create_user(
            email='admin@test.com', password='admin123', role=User.Roles.ADMIN, username='admin@test.com'
        )
        self.admin = Admin.objects.create(user=admin_user, name='Admin User', email='admin@test.com')
        staff_user = User.objects.create_user(
            email='staff@test.com', password='staff123', role=User.Roles.STAFF, username='staff@test.com'
        )
        self.staff = Staff.objects.create(user=staff_user, name='Staff User', phone='0100000000')
        self.admin_token = self._get_token('admin@test.com', 'admin123')
        self.staff_token = self._get_token('staff@test.com', 'staff123')

    def _get_token(self, email, password):
        resp = self.client.post('/api/users/login/', {'username': email, 'password': password})
        return resp.data['access']

    # --- Login ---
    def test_login_valid_staff(self):
        resp = self.client.post('/api/users/login/', {'username': 'staff@test.com', 'password': 'staff123'})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('access', resp.data)
        self.assertIn('refresh', resp.data)
        self.assertEqual(resp.data['role'], 'staff')

    def test_login_valid_admin(self):
        resp = self.client.post('/api/users/login/', {'username': 'admin@test.com', 'password': 'admin123'})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['role'], 'admin')

    def test_login_invalid_password(self):
        resp = self.client.post('/api/users/login/', {'username': 'staff@test.com', 'password': 'wrong'})
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_invalid_email(self):
        resp = self.client.post('/api/users/login/', {'username': 'noone@test.com', 'password': 'staff123'})
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    # --- Token Refresh ---
    def test_token_refresh(self):
        login = self.client.post('/api/users/login/', {'username': 'staff@test.com', 'password': 'staff123'})
        refresh = login.data['refresh']
        resp = self.client.post('/api/users/token/refresh/', {'refresh': refresh})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('access', resp.data)

    # --- Create Staff (Admin only) ---
    def test_create_staff_as_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        resp = self.client.post('/api/users/staff/', {'username': 'new@test.com', 'email': 'new@test.com', 'name': 'New Staff', 'phone': '0100000001', 'password': 'pass123', 'confirm_password': 'pass123'})
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Staff.objects.count(), 2)  # staff + new

    def test_create_staff_as_staff_forbidden(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.staff_token}')
        resp = self.client.post('/api/users/staff/', {'username': 'new@test.com', 'name': 'New Staff', 'password': 'pass123'})
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_staff_unauthenticated(self):
        resp = self.client.post('/api/users/staff/', {'username': 'new@test.com', 'name': 'New Staff', 'password': 'pass123'})
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    # --- Create Student ---
    def test_create_student_as_staff(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.staff_token}')
        resp = self.client.post('/api/users/students/', {'name': 'Ali', 'parent_contact': '01234567890', 'phone': '01234567890', 'email': 'ali@test.com'})
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_create_student_as_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        resp = self.client.post('/api/users/students/', {'name': 'Sara', 'parent_contact': '01234567891', 'phone': '01234567891', 'email': 'sara@test.com'})
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_create_student_duplicate_phone(self):
        Student.objects.create(name='First', parent_contact='000', phone='01234567890', email='first@test.com')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.staff_token}')
        resp = self.client.post('/api/users/students/', {'name': 'Second', 'parent_contact': '111', 'phone': '01234567890', 'email': 'second@test.com'})
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    # --- Delete Student ---
    def test_delete_student_as_staff(self):
        student = Student.objects.create(name='Del', parent_contact='000', phone='09999999999', email='del1@test.com')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.staff_token}')
        resp = self.client.delete(f'/api/users/students/{student.pk}/')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_student_as_admin(self):
        student = Student.objects.create(name='Del', parent_contact='000', phone='09999999998', email='del2@test.com')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        resp = self.client.delete(f'/api/users/students/{student.pk}/')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    # --- Create Teacher ---
    def test_create_teacher_as_staff(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.staff_token}')
        resp = self.client.post('/api/users/teachers/', {'name': 'Mr. Test', 'phone': '01000000000', 'email': 'mr.test@test.com'})
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
