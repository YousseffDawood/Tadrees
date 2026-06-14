from django.test import TestCase
from django.contrib.auth.hashers import make_password
from rest_framework.test import APIClient
from rest_framework import status
from users.models import Staff, Admin, User
from .models import CenterInfo, Announcement


class CenterAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        staff_user = User.objects.create_user(
            email='staff@cen.com', password='pass123', role=User.Roles.STAFF, username='staff@cen.com'
        )
        self.staff = Staff.objects.create(user=staff_user, name='Staff Cen', phone='0100000003')
        admin_user = User.objects.create_user(
            email='admin@cen.com', password='pass123', role=User.Roles.ADMIN, username='admin@cen.com'
        )
        self.admin = Admin.objects.create(user=admin_user, name='Admin Cen', email='admin@cen.com')
        login_staff = self.client.post('/api/users/login/', {'username': 'staff@cen.com', 'password': 'pass123'})
        self.token = login_staff.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

    # --- CenterInfo ---
    def test_create_center_info(self):
        resp = self.client.post('/api/center/center-info/', {
            'center_name': 'Tadrees Center', 'contact': 'info@tadrees.com'
        })
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_list_center_info(self):
        CenterInfo.objects.create(center_name='Test Center')
        resp = self.client.get('/api/center/center-info/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_update_center_info(self):
        ci = CenterInfo.objects.create(center_name='Old Name')
        resp = self.client.patch(f'/api/center/center-info/{ci.pk}/', {'center_name': 'New Name'})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_delete_center_info(self):
        ci = CenterInfo.objects.create(center_name='Del')
        resp = self.client.delete(f'/api/center/center-info/{ci.pk}/')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    # --- Announcement ---
    def test_create_announcement(self):
        resp = self.client.post('/api/center/announcements/', {
            'target': 'all', 'title': 'Hello', 'content': 'Welcome'
        })
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        ann = Announcement.objects.last()
        self.assertEqual(ann.announcer.pk, self.staff.user.pk)
        self.assertEqual(ann.announcer.email, 'staff@cen.com')

    def test_create_announcement_as_admin(self):
        self.client.credentials()
        login_admin = self.client.post('/api/users/login/', {'username': 'admin@cen.com', 'password': 'pass123'})
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {login_admin.data["access"]}')
        resp = self.client.post('/api/center/announcements/', {
            'target': 'staff_only', 'title': 'Admin Msg', 'content': 'For staff eyes'
        })
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        ann = Announcement.objects.last()
        self.assertEqual(ann.announcer.pk, self.admin.user.pk)

    def test_create_announcement_sends_target(self):
        resp = self.client.post('/api/center/announcements/', {
            'target': 'students_only', 'title': 'Study', 'content': 'Exam next week'
        })
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Announcement.objects.last().target, 'students_only')

    def test_list_announcements(self):
        Announcement.objects.create(
            announcer=self.staff.user, target='all', title='T', content='C'
        )
        resp = self.client.get('/api/center/announcements/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_unauthenticated_blocked(self):
        self.client.credentials()
        resp = self.client.get('/api/center/announcements/')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)
