from django.db import models
from academics.models import Schedule, SpecialSchedule
from users.models import Student


class Session(models.Model):
    schedule = models.ForeignKey(
        Schedule, on_delete=models.CASCADE,
        null=True, blank=True, related_name='sessions'
    )
    special_schedule = models.ForeignKey(
        SpecialSchedule, on_delete=models.CASCADE,
        null=True, blank=True, related_name='sessions'
    )
    notes = models.TextField(blank=True, default='')
    cancelled = models.BooleanField(default=False)
    session_date = models.DateField()
    students_attended = models.ManyToManyField(Student, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['schedule', 'session_date'],
                condition=models.Q(schedule__isnull=False),
                name='unique_session_per_schedule_date'
            ),
            models.UniqueConstraint(
                fields=['special_schedule', 'session_date'],
                condition=models.Q(special_schedule__isnull=False),
                name='unique_session_per_special_date'
            ),
        ]

    @property
    def source(self):
        return self.special_schedule or self.schedule

    @property
    def price(self):
        if self.special_schedule_id:
            return self.special_schedule.price
        return self.schedule.subject.price

    @property
    def subject(self):
        return self.source.subject

    @property
    def teacher(self):
        return self.source.teacher

    @property
    def room(self):
        return self.source.room

    @property
    def is_special(self):
        return self.special_schedule_id is not None

    def __str__(self):
        kind = 'special' if self.is_special else 'regular'
        return f'{self.subject.name} on {self.session_date} ({kind})'
