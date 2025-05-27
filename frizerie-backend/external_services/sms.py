from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from config.settings import get_settings
import logging
from typing import Optional, Tuple

# Set up logging
logger = logging.getLogger(__name__)

def send_sms(
    to_phone_number: str,
    body: str
) -> Tuple[bool, Optional[str]]:
    """
    Sends an SMS message using Twilio.
    
    Args:
        to_phone_number: The recipient's phone number
        body: The message content
        
    Returns:
        Tuple[bool, Optional[str]]: (success status, error message if any)
    """
    settings = get_settings()
    account_sid = settings.TWILIO_ACCOUNT_SID
    auth_token = settings.TWILIO_AUTH_TOKEN
    twilio_phone_number = settings.TWILIO_PHONE_NUMBER

    if not all([account_sid, auth_token, twilio_phone_number]):
        error_msg = "Missing Twilio credentials. Please check your environment variables."
        logger.error(error_msg)
        return False, error_msg

    try:
        client = Client(account_sid, auth_token)
        message = client.messages.create(
            body=body,
            from_=twilio_phone_number,
            to=to_phone_number
        )
        logger.info(f"SMS sent successfully to {to_phone_number}: {message.sid}")
        return True, None
    except TwilioRestException as e:
        error_msg = f"Twilio error: {str(e)}"
        logger.error(error_msg)
        return False, error_msg
    except Exception as e:
        error_msg = f"Unexpected error sending SMS: {str(e)}"
        logger.error(error_msg)
        return False, error_msg 