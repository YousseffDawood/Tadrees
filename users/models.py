from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    class Roles(models.TextChoices):
        ADMIN='ADMIN','Admin'
        STAFF='STAFF','Staff'

    role = models.CharField(max_length=10, choices=Roles.choices, default=Roles.STAFF)
    email = models.EmailField(unique=True)

class Staff(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=100, blank=True)


class Admin(models.Model):
    user=models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    center_info = models.CharField(max_length=255, unique=True)
    phone = models.CharField(max_length=20, unique=True)
    def __str__(self):
        return f'{self.name} (Admin)'


class Teacher(models.Model):
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20,unique=True)
    email = models.EmailField(unique=True)
    description = models.TextField(blank=True)
    photo = models.ImageField(upload_to='teachers/', blank=True, null=True)

    def __str__(self):
        return self.name


class Student(models.Model):
    name = models.CharField(max_length=255)
    grade = models.CharField(max_length=50, null=True, blank=True)
    parent_contact = models.CharField(max_length=20)
    phone = models.CharField(max_length=20, unique=True)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.name
