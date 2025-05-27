import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from config.settings import get_settings

def send_email(
    to_email: str,
    subject: str,
    body: str
):
    """Sends an email using the configured SMTP settings."""
    settings = get_settings()
    message = MIMEMultipart()
    message['From'] = f"{settings.MAIL_FROM_NAME} <{settings.MAIL_FROM}>"
    message['To'] = to_email
    message['Subject'] = subject

    message.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP(settings.MAIL_SERVER, settings.MAIL_PORT) as server:
            server.starttls() # Secure the connection
            server.login(settings.MAIL_USERNAME, settings.MAIL_PASSWORD)
            server.sendmail(settings.MAIL_FROM, to_email, message.as_string())
        print(f"Email sent successfully to {to_email}")
    except Exception as e:
        print(f"Failed to send email to {to_email}: {e}") 