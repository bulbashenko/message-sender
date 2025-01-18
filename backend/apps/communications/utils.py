import requests
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import Communication


def send_whatsapp_message(to_number: str, message: str = None, message_type: str = "text", user = None) -> dict:
    try:
        url = f"https://graph.facebook.com/v21.0/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
        headers = {
            "Authorization": f"Bearer {settings.WHATSAPP_ACCESS_TOKEN}",
            "Content-Type": "application/json",
        }

        if message_type == "template":
            data = {
                "messaging_product": "whatsapp",
                "to": to_number,
                "type": "template",
                "template": {
                    "name": "hello_world",
                    "language": {
                        "code": "en_US"
                    }
                }
            }
        else:
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


    return result


def send_email_message(to_email: str, subject: str, message: str, user) -> dict:
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


    return result
