from datetime import datetime, timedelta
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from users.models import Teacher, Student
from .utils import check_overlap, generate_sessions


class Room(models.Model):
    name = models.CharField(max_length=50)
    capacity = models.PositiveIntegerField()

    def __str__(self):
        return self.name


class Subject(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    teacher = models.ManyToManyField(Teacher, blank=True)

    def __str__(self):
        return self.name


class Schedule(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='schedules')
    teacher = models.ForeignKey(
        Teacher, on_delete=models.CASCADE, related_name='schedules'
    )
    room = models.ForeignKey(Room, on_delete=models.PROTECT, related_name='schedules')
    start_date = models.DateField()
    time_start = models.TimeField()
    duration_in_minutes = models.PositiveIntegerField()

    class Meta:
        ordering = ['start_date', 'time_start']

    @property
    def day(self):
        return self.start_date.strftime('%A').upper()

    @property
    def time_end(self):
        dummy = datetime(2000, 1, 1)
        return (
            datetime.combine(dummy, self.time_start)
            + timedelta(minutes=self.duration_in_minutes)
        ).time()

    def clean(self):
        if not self.teacher_id or not self.room_id:
            return
        check_overlap(
            date_val=self.start_date,
            time_start=self.time_start,
            duration_minutes=self.duration_in_minutes,
            room=self.room,
            teacher=self.teacher,
            exclude_schedule_pk=self.pk,
        )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.subject} \u2014 {self.day} {self.time_start}'


class SpecialSchedule(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='special_schedules')
    teacher = models.ForeignKey(
        Teacher, on_delete=models.CASCADE, related_name='special_schedules'
    )
    room = models.ForeignKey(Room, on_delete=models.PROTECT, related_name='special_schedules')
    start_date = models.DateField()
    time_start = models.TimeField()
    duration_in_minutes = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    note = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ['start_date', 'time_start']

    @property
    def day(self):
        return self.start_date.strftime('%A').upper()

    @property
    def time_end(self):
        dummy = datetime(2000, 1, 1)
        return (
            datetime.combine(dummy, self.time_start)
            + timedelta(minutes=self.duration_in_minutes)
        ).time()

    def clean(self):
        if not self.teacher_id or not self.room_id:
            return
        check_overlap(
            date_val=self.start_date,
            time_start=self.time_start,
            duration_minutes=self.duration_in_minutes,
            room=self.room,
            teacher=self.teacher,
            exclude_special_pk=self.pk,
        )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.subject} \u2014 {self.start_date} {self.time_start} (special)'


class Enrollment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='enrollments')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='enrollments')
    paid = models.BooleanField(default=False)
    date_enrollment = models.DateField(auto_now_add=True)
    handled_by = models.CharField(max_length=255)

    class Meta:
        unique_together = ('student', 'subject')

    def __str__(self):
        return f'{self.student.name} \u2192 {self.subject.name}'


# --- auto-generate sessions when a Schedule is created ---

@receiver(post_save, sender=Schedule)
def on_schedule_saved(sender, instance, created, **kwargs):
    if created:
        generate_sessions(instance)
