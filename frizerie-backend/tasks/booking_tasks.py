from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from config.database import SessionLocal
from bookings import models # Import booking models
from bookings.services import send_booking_reminder, send_booking_feedback_request
from notifications.services import send_last_minute_availability_notifications # Import the new notification function
from .celery_app import celery_app
import logging

logger = logging.getLogger(__name__)

@celery_app.task(name="schedule_booking_reminders")
def schedule_booking_reminders():
    """
    Schedule reminders for bookings happening in the next 24 hours.
    This task should be run daily.
    """
    db = None # Initialize db to None
    try:
        db = SessionLocal()
        # Get all confirmed bookings happening in the next 24 hours
        now = datetime.now()
        tomorrow = now + timedelta(days=1)
        
        bookings = db.query(models.Booking).filter(
            models.Booking.status == "CONFIRMED",
            models.Booking.start_time >= now,
            models.Booking.start_time <= tomorrow
        ).all()
        
        for booking in bookings:
            send_booking_reminder(db, booking.id)
            
    except Exception as e:
        logger.error(f"Error scheduling booking reminders: {str(e)}")
    finally:
        if db:
            db.close()

@celery_app.task(name="schedule_feedback_requests")
def schedule_feedback_requests():
    """
    Schedule feedback requests for completed bookings.
    This task should be run daily.
    """
    db = None # Initialize db to None
    try:
        db = SessionLocal()
        # Get all confirmed bookings that ended in the last 24 hours
        now = datetime.now()
        yesterday = now - timedelta(days=1)
        
        bookings = db.query(models.Booking).filter(
            models.Booking.status == "CONFIRMED",
            models.Booking.end_time >= yesterday,
            models.Booking.end_time <= now
        ).all()
        
        for booking in bookings:
            send_booking_feedback_request(db, booking.id)
            
    except Exception as e:
        logger.error(f"Error scheduling feedback requests: {str(e)}")
    finally:
        if db:
            db.close()

@celery_app.task(name="check_for_last_minute_availability")
def check_for_last_minute_availability():
    """
    Checks for recently cancelled bookings and sends last-minute availability alerts.
    This task should be run periodically (e.g., every hour).
    """
    db = None # Initialize db to None
    try:
        db = SessionLocal()
        # Define the time window for recently cancelled bookings (e.g., last hour)
        time_window = datetime.now() - timedelta(hours=1)

        # Query for bookings cancelled within the last hour
        # Assuming you have a 'cancelled_at' timestamp on the Booking model
        # If not, you might need to track cancellations differently
        recently_cancelled_bookings = db.query(models.Booking).filter(
            models.Booking.status == "CANCELLED",
            models.Booking.updated_at >= time_window # Using updated_at as a proxy for cancellation time
        ).all()

        for booking in recently_cancelled_bookings:
            # Retrieve service and stylist details for the notification
            # You might need to fetch these relationships if not already loaded
            service = booking.service # Assuming a relationship exists
            stylist = booking.stylist # Assuming a relationship exists

            if service and stylist:
                 booking_details = {
                    "service_name": service.name,
                    "stylist_name": stylist.name,
                    "date": booking.start_time.strftime('%Y-%m-%d'),
                    "time": booking.start_time.strftime('%H:%M'),
                    "start_time": booking.start_time,
                    "end_time": booking.end_time
                }
                 send_last_minute_availability_notifications(db, booking_details)
            else:
                logger.warning(f"Could not retrieve service or stylist details for cancelled booking {booking.id}.")

    except Exception as e:
        logger.error(f"Error checking for last-minute availability: {str(e)}")
    finally:
        if db:
            db.close() 