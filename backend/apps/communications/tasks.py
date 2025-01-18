import os
from django.utils import timezone
from config.celery import app
from .utils import send_email_message, send_whatsapp_message
from .models import Communication


@app.task(name='communications.send_email_async', bind=True)
def send_email_async(self, to_email: str, subject: str, message: str, user_id: int, comm_id: int):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    user = User.objects.get(id=user_id)

    comm = Communication.objects.get(id=comm_id)

    try:
        result = send_email_message(to_email, subject, message, user)
        success = result["status"] == "sent"
        
        comm.status = "sent" if success else "failed"
        if success:
            comm.sent_at = timezone.now()
        if result.get("error"):
            comm.error_message = result["error"]
        comm.save()

        return {
            "status": "success" if success else "error",
            "recipient": to_email,
            "error": result.get("error")
        }
    except Exception as e:
        comm.status = "failed"
        comm.error_message = str(e)
        comm.save()
        return {"status": "error", "error": str(e), "recipient": to_email}


@app.task(name='communications.send_whatsapp_async', bind=True)
def send_whatsapp_async(self, to_number: str, message_type: str = "text", message: str = None, user_id: int = None, comm_id: int = None):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    user = User.objects.get(id=user_id)

    comm = Communication.objects.get(id=comm_id)

    try:
        result = send_whatsapp_message(to_number, message, message_type, user)
        success = result["status"] == "sent"
        
        comm.status = "sent" if success else "failed"
        if success:
            comm.sent_at = timezone.now()
            comm.whatsapp_message_id = result.get("whatsapp_message_id")
        if result.get("error"):
            comm.error_message = result["error"]
        comm.save()

        return {
            "status": "success" if success else "error",
            "recipient": to_number,
            "whatsapp_message_id": result.get("whatsapp_message_id"),
            "error": result.get("error")
        }
    except Exception as e:
        comm.status = "failed"
        comm.error_message = str(e)
        comm.save()
        return {"status": "error", "error": str(e), "recipient": to_number}