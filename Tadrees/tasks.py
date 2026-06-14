from celery import shared_task
from datetime import date, timedelta
from academics.models import Schedule
from attendance.models import Session


@shared_task
def generate_todays_sessions():
    today = date.today()
    day_name = today.strftime('%A').upper()

    matching_schedules = [
        s for s in Schedule.objects.all()
        if s.day == day_name and s.start_date <= today
    ]

    for schedule in matching_schedules:
        Session.objects.get_or_create(
            schedule=schedule,
            session_date=today
        )


@shared_task
def cleanup_old_sessions():
    cutoff = date.today() - timedelta(days=30)
    sessions = Session.objects.filter(session_date__lt=cutoff)
    count = sessions.count()
    sessions.delete()
    return f'Deleted {count} old sessions'


@shared_task
def clean_old_special_schedules():
    from academics.models import SpecialSchedule
    cutoff = date.today() - timedelta(days=7)
    SpecialSchedule.objects.filter(start_date__lt=cutoff).delete()
