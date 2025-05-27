import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config.settings import get_settings
from .celery_app import celery_app

settings = get_settings()

@celery_app.task(name="send_email_notification")
async def send_email_notification(
    to_email: str,
    subject: str,
    html_content: str,
    text_content: str = None
) -> bool:
    """
    Send an email notification using SMTP.
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        html_content: HTML content of the email
        text_content: Plain text content of the email (optional)
    
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    try:
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = settings.SMTP_FROM_EMAIL
        message["To"] = to_email

        # Attach HTML content
        html_part = MIMEText(html_content, "html")
        message.attach(html_part)

        # Attach text content if provided
        if text_content:
            text_part = MIMEText(text_content, "plain")
            message.attach(text_part)

        # Send email
        async with aiosmtplib.SMTP(
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            use_tls=settings.SMTP_USE_TLS
        ) as smtp:
            await smtp.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            await smtp.send_message(message)

        return True
    except Exception as e:
        # Log the error
        print(f"Failed to send email: {str(e)}")
        return False

@celery_app.task(name="send_booking_confirmation")
async def send_booking_confirmation(
    to_email: str,
    booking_details: dict
) -> bool:
    """
    Send a booking confirmation email.
    
    Args:
        to_email: Recipient email address
        booking_details: Dictionary containing booking information
    
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    subject = "Booking Confirmation"
    html_content = f"""
    <html>
        <body>
            <h1>Booking Confirmation</h1>
            <p>Your booking has been confirmed:</p>
            <ul>
                <li>Service: {booking_details['service_type']}</li>
                <li>Date: {booking_details['booking_time']}</li>
                <li>Duration: {booking_details['duration']} minutes</li>
            </ul>
            <p>Thank you for choosing our services!</p>
        </body>
    </html>
    """
    
    return await send_email_notification(to_email, subject, html_content)

@celery_app.task(name="send_booking_reminder")
async def send_booking_reminder(
    to_email: str,
    booking_details: dict
) -> bool:
    """
    Send a booking reminder email.
    
    Args:
        to_email: Recipient email address
        booking_details: Dictionary containing booking information
    
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    subject = "Booking Reminder"
    html_content = f"""
    <html>
        <body>
            <h1>Booking Reminder</h1>
            <p>This is a reminder for your upcoming booking:</p>
            <ul>
                <li>Service: {booking_details['service_type']}</li>
                <li>Date: {booking_details['booking_time']}</li>
                <li>Duration: {booking_details['duration']} minutes</li>
            </ul>
            <p>We look forward to seeing you!</p>
        </body>
    </html>
    """
    
    return await send_email_notification(to_email, subject, html_content) 