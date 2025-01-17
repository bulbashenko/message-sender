import requests
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import Communication


def send_whatsapp_message(to_number: str, message: str, user) -> dict:
    """
    Send WhatsApp message and return delivery status.
    No message history is maintained - records are deleted after delivery attempt.
    """
    comm = Communication(
        type="whatsapp",
        recipient=to_number,
        content=message,
        status="pending",
        user=user
    )
    comm.save()

    result = {}
    try:
        url = f"https://graph.facebook.com/v21.0/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
        headers = {
            "Authorization": f"Bearer {settings.WHATSAPP_ACCESS_TOKEN}",
            "Content-Type": "application/json",
        }

        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to_number,
            "type": "text",
            "text": {
                "body": message
            }
        }

        response = requests.post(url, headers=headers, json=data)
        response_data = response.json()

        if response.status_code in [200, 201]:
            if "messages" in response_data and len(response_data["messages"]) > 0:
                result = {
                    "status": "sent",
                    "whatsapp_message_id": response_data["messages"][0]["id"]
                }
        else:
            result = {
                "status": "failed",
                "error": f"API Error: {response.text}"
            }

    except Exception as e:
        result = {
            "status": "failed",
            "error": str(e)
        }

    # Delete the communication record as we don't maintain history
    comm.delete()
    return result


def send_email_message(to_email: str, subject: str, message: str, user) -> dict:
    """
    Send email message and return delivery status.
    No message history is maintained - records are deleted after delivery attempt.
    """
    comm = Communication(
        type="email",
        recipient=to_email,
        subject=subject,
        content=message,
        status="pending",
        user=user
    )
    comm.save()

    result = {}
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[to_email],
            fail_silently=False,
        )
        result = {"status": "sent"}

    except Exception as e:
        result = {
            "status": "failed",
            "error": str(e)
        }

    # Delete the communication record as we don't maintain history
    comm.delete()
    return result
