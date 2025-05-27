from celery import Celery
from config.settings import get_settings

settings = get_settings()

celery_app = Celery(
    "frizerie",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "tasks.email_tasks",
        "tasks.sms_tasks",
        "tasks.push_tasks",
        "tasks.booking_tasks"
    ]
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour
    worker_max_tasks_per_child=1000,
    worker_prefetch_multiplier=1,
    
    # Add beat schedule for periodic tasks
    beat_schedule={
        'schedule-booking-reminders': {
            'task': 'tasks.booking_tasks.schedule_booking_reminders',
            'schedule': 86400.0,  # Run daily (24 hours)
        },
        'schedule-feedback-requests': {
            'task': 'tasks.booking_tasks.schedule_feedback_requests',
            'schedule': 86400.0,  # Run daily (24 hours)
        },
        'check-for-last-minute-availability': {
            'task': 'tasks.booking_tasks.check_for_last_minute_availability',
            'schedule': 3600.0,  # Run hourly (3600 seconds)
        },
    }
) 