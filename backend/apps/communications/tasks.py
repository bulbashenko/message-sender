import os
from config.celery import app
from .utils import send_email_message, send_whatsapp_message


@app.task(name='communications.send_email_async', bind=True)
def send_email_async(self, to_email: str, subject: str, message: str, user_id: int):
    """
    Async task to send email messages.
    No message history is maintained - status is returned immediately.
    """
    from django.contrib.auth import get_user_model
    User = get_user_model()
    user = User.objects.get(id=user_id)

    try:
        result = send_email_message(to_email, subject, message, user)
        return {
            "status": "success" if result["status"] == "sent" else "error",
            "recipient": to_email,
            "error": result.get("error")
        }
    except Exception as e:
        return {"status": "error", "error": str(e), "recipient": to_email}


@app.task(name='communications.send_whatsapp_async', bind=True)
def send_whatsapp_async(self, to_number: str, message: str, user_id: int):
    """
    Async task to send WhatsApp messages.
    No message history is maintained - status is returned immediately.
    """
    from django.contrib.auth import get_user_model
    User = get_user_model()
    user = User.objects.get(id=user_id)

    try:
        result = send_whatsapp_message(to_number, message, user)
        return {
            "status": "success" if result["status"] == "sent" else "error",
            "recipient": to_number,
            "whatsapp_message_id": result.get("whatsapp_message_id"),
            "error": result.get("error")
        }
    except Exception as e:
        return {"status": "error", "error": str(e), "recipient": to_number}
