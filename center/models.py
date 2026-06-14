from django.db import models


class CenterInfo(models.Model):
    center_name = models.CharField(max_length=255)
    logo = models.ImageField(upload_to='logos/', blank=True, null=True)
    description = models.TextField(blank=True)
    contact = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.center_name


class Announcement(models.Model):
    TARGET_CHOICES = [
        ('staff_only', 'Staff Only'),
        ('students_only', 'Students Only'),
        ('teachers_only', 'Teachers Only'),
        ('all', 'All'),
    ]

    announcer = models.ForeignKey('users.User', on_delete=models.CASCADE)
    target = models.CharField(max_length=20, choices=TARGET_CHOICES)
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.title} by {self.announcer.name}'
