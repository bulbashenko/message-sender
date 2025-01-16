from datetime import datetime
import requests
from django.core.mail import send_mail
from django.conf import settings
from .models import Communication


def send_whatsapp_message(to_number: str, message: str) -> Communication:
    """
    Send a WhatsApp message using Meta Cloud API and track it
    """
    # Create communication record with all required fields
    comm = Communication(
        type="whatsapp",
        recipient=to_number,
        content=message,
        status="pending",  # Explicitly set status
    )
    comm.save()  # Save the record

    try:
        # Prepare API request
        url = (
            f"{settings.WHATSAPP_API_URL}/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
        )
        headers = {
            "Authorization": f"Bearer {settings.WHATSAPP_ACCESS_TOKEN}",
            "Content-Type": "application/json",
        }

        data = {
            "messaging_product": "whatsapp",
            "to": to_number,
            "type": "text",
            "text": {"body": message},
        }

        # Send message
        response = requests.post(url, headers=headers, json=data)
        response_data = response.json()

        if response.status_code in [200, 201]:
            comm.status = "sent"
            comm.sent_at = datetime.now()
            # Store WhatsApp message ID for tracking
            if "messages" in response_data and len(response_data["messages"]) > 0:
                comm.whatsapp_message_id = response_data["messages"][0]["id"]
        else:
            comm.status = "failed"
            comm.error_message = f"API Error: {response.text}"

    except Exception as e:
        comm.status = "failed"
        comm.error_message = str(e)

    comm.save()
    return comm


def send_email_message(to_email: str, subject: str, message: str) -> Communication:
    """
    Send an email and track it in the Communication model
    """
    # Create communication record first with all required fields
    comm = Communication(
        type="email",
        recipient=to_email,
        subject=subject,
        content=message,
        status="pending",  # Explicitly set status
    )
    comm.save()  # Save the record

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[to_email],
            fail_silently=False,
        )

        comm.status = "sent"
        comm.sent_at = datetime.now()

    except Exception as e:
        comm.status = "failed"
        comm.error_message = str(e)

    comm.save()
    return comm
