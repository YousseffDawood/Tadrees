from django.db import models
from academics.models import Enrollment
from attendance.models import Session


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    type = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Payment(models.Model):
    enrollment = models.ForeignKey(
        Enrollment, on_delete=models.SET_NULL,
        null=True, blank=True
    )
    session = models.ForeignKey(
        Session, on_delete=models.SET_NULL,
        null=True, blank=True
    )
    product = models.ForeignKey(
        Product, on_delete=models.SET_NULL,
        null=True, blank=True
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_at = models.DateTimeField(auto_now_add=True)
    note = models.TextField(blank=True)
    handled_by = models.CharField(max_length=255)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['enrollment', 'session'],
                condition=models.Q(session__isnull=False),
                name='unique_payment_per_enrollment_session'
            ),
        ]

    def __str__(self):
        return f'Payment {self.id} - {self.amount}'
