from datetime import datetime, timedelta, date
from django.core.exceptions import ValidationError


def check_overlap(date_val, time_start, duration_minutes, room, teacher,
                  exclude_schedule_pk=None, exclude_special_pk=None):

    from .models import Schedule, SpecialSchedule

    dummy = datetime(2000, 1, 1)
    start = datetime.combine(dummy, time_start)
    end = start + timedelta(minutes=duration_minutes)
    weekday = date_val.strftime('%A').upper()

    def times_overlap(s):
        s_start = datetime.combine(dummy, s.time_start)
        s_end = s_start + timedelta(minutes=s.duration_in_minutes)
        return start < s_end and end > s_start

    def raise_if_conflict(s, label):
        if s.room_id == room.pk:
            raise ValidationError(f"Room '{room}' is already booked {label}.")
        if s.teacher_id == teacher.pk:
            raise ValidationError(f"Teacher '{teacher}' already has a class {label}.")

    # 1. Weekly schedules on the same weekday
    weekly_qs = Schedule.objects.exclude(pk=exclude_schedule_pk or 0)
    for s in weekly_qs:
        if s.start_date.strftime('%A').upper() == weekday and times_overlap(s):
            raise_if_conflict(s, f"every {weekday.capitalize()} at {time_start}")

    # 2. Special schedules on the exact same date
    special_qs = SpecialSchedule.objects.filter(start_date=date_val).exclude(pk=exclude_special_pk or 0)
    for s in special_qs:
        if times_overlap(s):
            raise_if_conflict(s, f"on {date_val}")


def generate_sessions(schedule, months_ahead=3):
    from attendance.models import Session

    today = date.today()
    end_date = today + timedelta(days=months_ahead * 30)
    weekday = schedule.start_date.weekday()

    days_ahead = (weekday - today.weekday()) % 7
    current = today + timedelta(days=days_ahead)

    sessions_to_create = []
    while current <= end_date:
        if current >= schedule.start_date:
            exists = Session.objects.filter(
                schedule=schedule,
                session_date=current
            ).exists()
            if not exists:
                sessions_to_create.append(
                    Session(schedule=schedule, session_date=current)
                )
        current += timedelta(weeks=1)

    Session.objects.bulk_create(sessions_to_create)
