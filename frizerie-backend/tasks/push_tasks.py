import firebase_admin
from firebase_admin import messaging
from config.settings import get_settings
from .celery_app import celery_app

settings = get_settings()

# Initialize Firebase Admin SDK
try:
    firebase_admin.get_app()
except ValueError:
    firebase_admin.initialize_app()

@celery_app.task(name="send_push_notification")
def send_push_notification(
    token: str,
    title: str,
    body: str,
    data: dict = None
) -> bool:
    """
    Send a push notification using Firebase Cloud Messaging.
    
    Args:
        token: Device registration token
        title: Notification title
        body: Notification body
        data: Additional data to send with the notification
    
    Returns:
        bool: True if notification was sent successfully, False otherwise
    """
    try:
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body
            ),
            data=data or {},
            token=token
        )
        
        response = messaging.send(message)
        return True
    except Exception as e:
        # Log the error
        print(f"Failed to send push notification: {str(e)}")
        return False

@celery_app.task(name="send_booking_push_confirmation")
def send_booking_push_confirmation(
    token: str,
    booking_details: dict
) -> bool:
    """
    Send a booking confirmation push notification.
    
    Args:
        token: Device registration token
        booking_details: Dictionary containing booking information
    
    Returns:
        bool: True if notification was sent successfully, False otherwise
    """
    title = "Booking Confirmed"
    body = (
        f"Your {booking_details['service_type']} booking has been confirmed "
        f"for {booking_details['booking_time']}"
    )
    
    data = {
        "type": "booking_confirmation",
        "booking_id": str(booking_details['id']),
        "service_type": booking_details['service_type'],
        "booking_time": booking_details['booking_time']
    }
    
    return send_push_notification(token, title, body, data)

@celery_app.task(name="send_booking_push_reminder")
def send_booking_push_reminder(
    token: str,
    booking_details: dict
) -> bool:
    """
    Send a booking reminder push notification.
    
    Args:
        token: Device registration token
        booking_details: Dictionary containing booking information
    
    Returns:
        bool: True if notification was sent successfully, False otherwise
    """
    title = "Booking Reminder"
    body = (
        f"Reminder: You have a {booking_details['service_type']} booking "
        f"tomorrow at {booking_details['booking_time']}"
    )
    
    data = {
        "type": "booking_reminder",
        "booking_id": str(booking_details['id']),
        "service_type": booking_details['service_type'],
        "booking_time": booking_details['booking_time']
    }
    
    return send_push_notification(token, title, body, data) 