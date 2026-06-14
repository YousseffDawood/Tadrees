from datetime import date, time, timedelta
from django.test import TestCase
from django.contrib.auth.hashers import make_password
from rest_framework.test import APIClient
from rest_framework import status
from users.models import Staff, Admin, Teacher, Student, User
from academics.models import Subject, Room, Schedule, Enrollment
from .models import Session


class SessionSignalTest(TestCase):
    def test_schedule_creates_sessions_on_save(self):
        room = Room.objects.create(name='R1', capacity=20)
        teacher = Teacher.objects.create(name='Mr. Smith', phone='123', email='smith@test.com')
        subject = Subject.objects.create(name='Math', description='Algebra', price=100.00)
        subject.teacher.add(teacher)
        today = date.today()
        days_until_monday = (7 - today.weekday()) % 7 or 7
        future_monday = today + timedelta(days=days_until_monday)
        schedule = Schedule.objects.create(
            subject=subject, teacher=teacher, room=room,
            start_date=future_monday, time_start=time(10, 0), duration_in_minutes=60,
        )
        session = Session.objects.filter(schedule=schedule, session_date=future_monday).first()
        self.assertIsNotNone(session, 'Session was not auto-created on Schedule save')
        self.assertEqual(session.session_date, future_monday)


class AttendanceAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        staff_user = User.objects.create_user(
            email='staff@att.com', password='pass123', role=User.Roles.STAFF, username='staff@att.com'
        )
        self.staff = Staff.objects.create(user=staff_user, name='Staff Att', phone='0100000002')
        login = self.client.post('/api/users/login/', {'username': 'staff@att.com', 'password': 'pass123'})
        self.token = login.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

        self.teacher = Teacher.objects.create(name='T. Att', phone='0100', email='t.att@test.com')
        self.student = Student.objects.create(name='S. Att', parent_contact='0100', phone='01000002', email='s.att@test.com')
        self.room = Room.objects.create(name='Att Room', capacity=20)
        self.subject = Subject.objects.create(name='Att Subj', description='Test', price='100.00')
        self.subject.teacher.add(self.teacher)

        # Create schedule (triggers session generation via signal)
        next_monday = date.today() + timedelta(days=(7 - date.today().weekday()) % 7 or 7)
        self.schedule = Schedule.objects.create(
            subject=self.subject, teacher=self.teacher, room=self.room,
            start_date=next_monday, time_start=time(9, 0), duration_in_minutes=60,
        )

    # --- Today's Sessions ---
    def test_today_sessions(self):
        resp = self.client.get('/api/attendance/sessions/today/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_today_sessions_unauthenticated(self):
        self.client.credentials()
        resp = self.client.get('/api/attendance/sessions/today/')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    # --- Attend ---
    def test_attend_student_enrolled_and_paid(self):
        Enrollment.objects.create(
            student=self.student, subject=self.subject, paid=True, handled_by='Staff'
        )
        # Get a session for this schedule
        session = Session.objects.filter(schedule=self.schedule).first()
        self.assertIsNotNone(session, 'No session found — signal may not have run')
        resp = self.client.post(f'/api/attendance/sessions/{session.pk}/attend/', {'phone_number': '01000002'})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn(self.student, session.students_attended.all())

    def test_attend_student_not_enrolled(self):
        session = Session.objects.filter(schedule=self.schedule).first()
        if not session:
            self.skipTest('No session available')
        resp = self.client.post(f'/api/attendance/sessions/{session.pk}/attend/', {'phone_number': '01000002'})
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_attend_student_not_paid(self):
        Enrollment.objects.create(
            student=self.student, subject=self.subject, paid=False, handled_by='Staff'
        )
        session = Session.objects.filter(schedule=self.schedule).first()
        if not session:
            self.skipTest('No session available')
        resp = self.client.post(f'/api/attendance/sessions/{session.pk}/attend/', {'phone_number': '01000002'})
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_attend_unknown_phone(self):
        session = Session.objects.filter(schedule=self.schedule).first()
        if not session:
            self.skipTest('No session available')
        resp = self.client.post(f'/api/attendance/sessions/{session.pk}/attend/', {'phone_number': '00000000000'})
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_attend_session_not_found(self):
        resp = self.client.post('/api/attendance/sessions/99999/attend/', {'phone_number': '01000002'})
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    # --- Attendance History ---
    def test_attendance_history_returns_past_sessions(self):
        Session.objects.create(schedule=self.schedule, session_date=date.today() - timedelta(days=5))
        resp = self.client.get('/api/attendance/sessions/history/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertGreater(len(resp.data), 0)
        for s in resp.data:
            self.assertLess(s['session_date'], date.today().isoformat())

    def test_attendance_history_excludes_future_sessions(self):
        future = date.today() + timedelta(days=30)
        Session.objects.create(schedule=self.schedule, session_date=future)
        resp = self.client.get('/api/attendance/sessions/history/')
        for s in resp.data:
            self.assertLess(s['session_date'], date.today().isoformat())

    def test_attendance_history_includes_students(self):
        past = Session.objects.create(schedule=self.schedule, session_date=date.today() - timedelta(days=5))
        past.students_attended.add(self.student)
        resp = self.client.get('/api/attendance/sessions/history/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        session_data = next(s for s in resp.data if s['id'] == past.pk)
        self.assertIn(self.student.name, [s['name'] for s in session_data['students_attended']])

    def test_attendance_history_unauthenticated(self):
        self.client.credentials()
        resp = self.client.get('/api/attendance/sessions/history/')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_attendance_history_ordered_by_date_desc(self):
        for i in range(3):
            Session.objects.create(
                schedule=self.schedule,
                session_date=date.today() - timedelta(days=i + 1)
            )
        resp = self.client.get('/api/attendance/sessions/history/')
        dates = [s['session_date'] for s in resp.data if s['session_date'] < date.today().isoformat()]
        self.assertEqual(dates, sorted(dates, reverse=True))
