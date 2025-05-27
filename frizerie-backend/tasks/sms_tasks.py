from twilio.rest import Client
from config.settings import get_settings
from .celery_app import celery_app

settings = get_settings()
twilio_client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

@celery_app.task(name="send_sms_notification")
def send_sms_notification(
    to_phone: str,
    message: str
) -> bool:
    """
    Send an SMS notification using Twilio.
    
    Args:
        to_phone: Recipient phone number
        message: SMS message content
    
    Returns:
        bool: True if SMS was sent successfully, False otherwise
    """
    try:
        message = twilio_client.messages.create(
            body=message,
            from_=settings.TWILIO_PHONE_NUMBER,
            to=to_phone
        )
        return True
    except Exception as e:
        # Log the error
        print(f"Failed to send SMS: {str(e)}")
        return False

@celery_app.task(name="send_booking_sms_confirmation")
def send_booking_sms_confirmation(
    to_phone: str,
    booking_details: dict
) -> bool:
    """
    Send a booking confirmation SMS.
    
    Args:
        to_phone: Recipient phone number
        booking_details: Dictionary containing booking information
    
    Returns:
        bool: True if SMS was sent successfully, False otherwise
    """
    message = (
        f"Your booking has been confirmed!\n"
        f"Service: {booking_details['service_type']}\n"
        f"Date: {booking_details['booking_time']}\n"
        f"Duration: {booking_details['duration']} minutes"
    )
    
    return send_sms_notification(to_phone, message)

@celery_app.task(name="send_booking_sms_reminder")
def send_booking_sms_reminder(
    to_phone: str,
    booking_details: dict
) -> bool:
    """
    Send a booking reminder SMS.
    
    Args:
        to_phone: Recipient phone number
        booking_details: Dictionary containing booking information
    
    Returns:
        bool: True if SMS was sent successfully, False otherwise
    """
    message = (
        f"Reminder: You have a booking tomorrow!\n"
        f"Service: {booking_details['service_type']}\n"
        f"Time: {booking_details['booking_time']}\n"
        f"Duration: {booking_details['duration']} minutes"
    )
    
    return send_sms_notification(to_phone, message) 