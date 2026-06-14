from datetime import date, time, timedelta
from django.test import TestCase
from django.contrib.auth.hashers import make_password
from rest_framework.test import APIClient
from rest_framework import status
from users.models import Staff, Admin, Teacher, Student, User
from academics.models import Subject, Room, Schedule, Enrollment
from .models import Product, Payment


class FinanceAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        admin_user = User.objects.create_user(
            email='admin@fin.com', password='pass123', role=User.Roles.ADMIN, username='admin@fin.com'
        )
        self.admin = Admin.objects.create(user=admin_user, name='Admin Fin', email='admin@fin.com')
        staff_user = User.objects.create_user(
            email='staff@fin.com', password='pass123', role=User.Roles.STAFF, username='staff@fin.com'
        )
        self.staff = Staff.objects.create(user=staff_user, name='Staff Fin', phone='0100000101')
        login_admin = self.client.post('/api/users/login/', {'username': 'admin@fin.com', 'password': 'pass123'})
        login_staff = self.client.post('/api/users/login/', {'username': 'staff@fin.com', 'password': 'pass123'})
        self.admin_token = login_admin.data['access']
        self.staff_token = login_staff.data['access']

    def _auth(self, token):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    # --- Product: Create (Staff + Admin) ---
    def test_create_product_as_staff(self):
        self._auth(self.staff_token)
        resp = self.client.post('/api/finance/products/', {'name': 'Book', 'description': 'A book', 'price': '50.00', 'type': 'book'})
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_create_product_as_admin(self):
        self._auth(self.admin_token)
        resp = self.client.post('/api/finance/products/', {'name': 'Pen', 'description': 'A pen', 'price': '5.00', 'type': 'supply'})
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    # --- Product: Update (Admin only) ---
    def test_update_product_as_admin(self):
        self._auth(self.admin_token)
        prod = Product.objects.create(name='Old', description='Old', price='10.00', type='book')
        resp = self.client.patch(f'/api/finance/products/{prod.pk}/', {'name': 'Updated'})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_update_product_as_staff_forbidden(self):
        self._auth(self.staff_token)
        prod = Product.objects.create(name='Old', description='Old', price='10.00', type='book')
        resp = self.client.patch(f'/api/finance/products/{prod.pk}/', {'name': 'Updated'})
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    # --- Product: Delete (Admin only) ---
    def test_delete_product_as_admin(self):
        self._auth(self.admin_token)
        prod = Product.objects.create(name='Del', description='D', price='1.00', type='book')
        resp = self.client.delete(f'/api/finance/products/{prod.pk}/')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_product_as_staff_forbidden(self):
        self._auth(self.staff_token)
        prod = Product.objects.create(name='Del', description='D', price='1.00', type='book')
        resp = self.client.delete(f'/api/finance/products/{prod.pk}/')
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    # --- Product: List ---
    def test_list_products(self):
        self._auth(self.staff_token)
        Product.objects.create(name='P1', description='D1', price='10.00', type='book')
        resp = self.client.get('/api/finance/products/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    # --- Payment (Staff + Admin) ---
    def test_create_payment_as_staff(self):
        self._auth(self.staff_token)
        teacher = Teacher.objects.create(name='T', phone='000', email='t@test.com')
        student = Student.objects.create(name='S', parent_contact='000', phone='00000001', email='s@test.com')
        room = Room.objects.create(name='R', capacity=10)
        subject = Subject.objects.create(name='Sub', description='D', price='100.00')
        subject.teacher.add(teacher)
        enrollment = Enrollment.objects.create(student=student, subject=subject, paid=False, handled_by='Staff')
        resp = self.client.post('/api/finance/payments/', {
            'enrollment': enrollment.pk, 'amount': '100.00',
            'note': 'Paid', 'staff_phone': '0100000101'
        })
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # Verify handled_by was set from staff name
        payment = Payment.objects.last()
        self.assertEqual(payment.handled_by, 'Staff Fin')

    def test_list_payments(self):
        self._auth(self.staff_token)
        resp = self.client.get('/api/finance/payments/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_unauthenticated_blocked(self):
        resp = self.client.get('/api/finance/products/')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)
