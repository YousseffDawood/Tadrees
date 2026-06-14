from django.db.models.signals import post_save
from django.dispatch import receiver
from academics.models import SpecialSchedule
from .models import Session


@receiver(post_save, sender=SpecialSchedule)
def create_session_for_special_schedule(sender, instance, created, **kwargs):
    if created:
        Session.objects.get_or_create(
            special_schedule=instance,
            session_date=instance.start_date
        )
