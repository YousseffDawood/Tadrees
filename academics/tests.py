from datetime import date, time, timedelta
from django.test import TestCase
from django.contrib.auth.hashers import make_password
from rest_framework.test import APIClient
from rest_framework import status
from users.models import Staff, Admin, Teacher, Student, User
from .models import Subject, Room, Schedule, SpecialSchedule, Enrollment


class AcademicsAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        admin_user = User.objects.create_user(
            email='admin@acad.com', password='pass123', role=User.Roles.ADMIN, username='admin@acad.com'
        )
        self.admin = Admin.objects.create(user=admin_user, name='Admin Acad', email='admin@acad.com')
        staff_user = User.objects.create_user(
            email='staff@acad.com', password='pass123', role=User.Roles.STAFF, username='staff@acad.com'
        )
        self.staff = Staff.objects.create(user=staff_user, name='Staff Acad', phone='0100000001')
        login_admin = self.client.post('/api/users/login/', {'username': 'admin@acad.com', 'password': 'pass123'})
        login_staff = self.client.post('/api/users/login/', {'username': 'staff@acad.com', 'password': 'pass123'})
        self.admin_token = login_admin.data['access']
        self.staff_token = login_staff.data['access']

        self.teacher = Teacher.objects.create(name='T. Acad', phone='0100', email='t.acad@test.com')
        self.student = Student.objects.create(name='S. Acad', parent_contact='0100', phone='01000001', email='s.acad@test.com')
        self.room = Room.objects.create(name='R1', capacity=20)

    def _auth(self, token):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    # --- Room ---
    def test_create_room(self):
        self._auth(self.staff_token)
        resp = self.client.post('/api/academics/rooms/', {'name': 'New Room', 'capacity': 30})
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_list_rooms(self):
        self._auth(self.staff_token)
        resp = self.client.get('/api/academics/rooms/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    # --- Subject ---
    def test_create_subject(self):
        self._auth(self.staff_token)
        resp = self.client.post('/api/academics/subjects/', {'name': 'Math', 'description': 'Algebra', 'price': '200.00'})
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_subject_add_teacher(self):
        self._auth(self.staff_token)
        subj = Subject.objects.create(name='Phys', description='Mech', price='150.00')
        resp = self.client.patch(f'/api/academics/subjects/{subj.pk}/', {'teacher': [self.teacher.pk]}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    # --- Schedule ---
    def test_create_schedule(self):
        self._auth(self.staff_token)
        subj = Subject.objects.create(name='Bio', description='Cells', price='180.00')
        subj.teacher.add(self.teacher)
        tomorrow = date.today() + timedelta(days=1)
        resp = self.client.post('/api/academics/schedules/', {
            'subject': subj.pk, 'teacher': self.teacher.pk, 'room': self.room.pk,
            'start_date': tomorrow.isoformat(), 'time_start': '10:00:00', 'duration_in_minutes': 60
        })
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_schedule_overlap_raises_error(self):
        self._auth(self.staff_token)
        subj = Subject.objects.create(name='Chem', description='Rxns', price='200.00')
        subj.teacher.add(self.teacher)
        tomorrow = date.today() + timedelta(days=1)
        # Create first schedule
        self.client.post('/api/academics/schedules/', {
            'subject': subj.pk, 'teacher': self.teacher.pk, 'room': self.room.pk,
            'start_date': tomorrow.isoformat(), 'time_start': '10:00:00', 'duration_in_minutes': 60
        })
        # Create overlapping schedule — same room, same time
        resp = self.client.post('/api/academics/schedules/', {
            'subject': subj.pk, 'teacher': self.teacher.pk, 'room': self.room.pk,
            'start_date': tomorrow.isoformat(), 'time_start': '10:30:00', 'duration_in_minutes': 60
        })
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_schedules(self):
        self._auth(self.staff_token)
        resp = self.client.get('/api/academics/schedules/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    # --- SpecialSchedule ---
    def test_create_special_schedule(self):
        self._auth(self.staff_token)
        subj = Subject.objects.create(name='Hist', description='Ancient', price='100.00')
        subj.teacher.add(self.teacher)
        tomorrow = date.today() + timedelta(days=1)
        resp = self.client.post('/api/academics/special-schedules/', {
            'subject': subj.pk, 'teacher': self.teacher.pk, 'room': self.room.pk,
            'start_date': tomorrow.isoformat(), 'time_start': '14:00:00',
            'duration_in_minutes': 90, 'price': '300.00', 'note': 'Workshop'
        })
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    # --- Enrollment ---
    def test_create_enrollment(self):
        self._auth(self.staff_token)
        subj = Subject.objects.create(name='Geo', description='Earth', price='120.00')
        subj.teacher.add(self.teacher)
        resp = self.client.post('/api/academics/enrollments/', {
            'student': self.student.pk, 'subject': subj.pk, 'paid': True, 'handled_by': 'Staff Acad'
        })
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_enrollment_unique_together(self):
        self._auth(self.staff_token)
        subj = Subject.objects.create(name='Astro', description='Stars', price='250.00')
        subj.teacher.add(self.teacher)
        self.client.post('/api/academics/enrollments/', {
            'student': self.student.pk, 'subject': subj.pk, 'paid': True, 'handled_by': 'Staff Acad'
        })
        resp = self.client.post('/api/academics/enrollments/', {
            'student': self.student.pk, 'subject': subj.pk, 'paid': False, 'handled_by': 'Staff Acad'
        })
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    # --- Unauthenticated ---
    def test_unauthenticated_blocked(self):
        resp = self.client.get('/api/academics/rooms/')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)
