import os
from celery import shared_task
from .utils import send_email_message, send_whatsapp_message


@shared_task
def send_email_async(to_email: str, subject: str, message: str):
    """
    Asynchronously send an email and track it
    """
    try:
        communication = send_email_message(to_email, subject, message)
        return {
            "status": "success",
            "communication_id": communication.id,
            "recipient": to_email,
        }
    except Exception as e:
        return {"status": "error", "error": str(e), "recipient": to_email}


@shared_task
def send_whatsapp_async(to_number: str, message: str):
    """
    Asynchronously send a WhatsApp message and track it
    """
    try:
        communication = send_whatsapp_message(to_number, message)
        return {
            "status": "success",
            "communication_id": communication.id,
            "recipient": to_number,
            "whatsapp_message_id": communication.whatsapp_message_id,
        }
    except Exception as e:
        return {"status": "error", "error": str(e), "recipient": to_number}
