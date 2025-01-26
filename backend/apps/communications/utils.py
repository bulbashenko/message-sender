import requests
from typing import Optional, Dict, Any, List
from django.core.mail import get_connection, EmailMessage
from django.conf import settings
from django.utils import timezone
from django.db.models import F
from django.core.cache import cache
from django.db import transaction
from .models import Communication, SMTPServer, WhatsAppAccount

CACHE_TTL = 3600
BATCH_SIZE = 50


def get_available_smtp_server() -> Optional[SMTPServer]:
    today = timezone.now().date()
    
    reset_needed = SMTPServer.objects.filter(last_reset_date__lt=today).exists()
    if reset_needed:
        SMTPServer.objects.filter(last_reset_date__lt=today).update(
            messages_sent_today=0,
            last_reset_date=today
        )
        cache.delete('available_smtp_servers')
    
    cache_key = 'available_smtp_servers'
    available_servers = cache.get(cache_key)
    
    if available_servers is None:
        available_servers = list(SMTPServer.objects.filter(
            is_active=True,
            messages_sent_today__lt=F('daily_limit')
        ).order_by('messages_sent_today').values('id', 'messages_sent_today'))
        
        if available_servers:
            cache.set(cache_key, available_servers, 300)
    
    if not available_servers:
        return None
    
    server_id = available_servers[0]['id']
    return SMTPServer.objects.get(id=server_id)


def get_available_whatsapp_account() -> Optional[WhatsAppAccount]:
    today = timezone.now().date()
    
    WhatsAppAccount.objects.filter(last_reset_date__lt=today).update(
        messages_sent_today=0,
        last_reset_date=today
    )
    
    available_accounts = WhatsAppAccount.objects.filter(
        is_active=True,
        messages_sent_today__lt=F('daily_limit')
    ).order_by('messages_sent_today')
    
    return available_accounts.first()


def send_whatsapp_message(to_number: str, message: str = None, message_type: str = "text", user = None) -> Dict[str, Any]:
    try:
        account = get_available_whatsapp_account()
        if not account:
            return {
                "status": "failed",
                "error": "No available WhatsApp accounts with remaining capacity"
            }

        url = f"https://graph.facebook.com/v21.0/{account.phone_number_id}/messages"
        headers = {
            "Authorization": f"Bearer {account.access_token}",
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
                account.messages_sent_today = F('messages_sent_today') + 1
                account.save()
                
                result = {
                    "status": "sent",
                    "whatsapp_message_id": response_data["messages"][0]["id"],
                    "account": account.id
                }
        else:
            result = {
                "status": "failed",
                "error": f"API Error: {response.text}",
                "account": account.id
            }

    except Exception as e:
        result = {
            "status": "failed",
            "error": str(e)
        }

    return result


def send_email_message(to_email: str, subject: str, message: str, user) -> Dict[str, Any]:
    try:
        server = get_available_smtp_server()
        if not server:
            return {
                "status": "failed",
                "error": "No available SMTP servers with remaining capacity"
            }

        connection = get_connection(
            host=server.host,
            port=server.port,
            username=server.username,
            password=server.password,
            use_tls=server.use_tls
        )

        email = EmailMessage(
            subject=subject,
            body=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[to_email],
            connection=connection,
        )
        
        email.send()

        server.messages_sent_today = F('messages_sent_today') + 1
        server.save()

        result = {
            "status": "sent",
            "server": server.id
        }

    except Exception as e:
        result = {
            "status": "failed",
            "error": str(e)
        }

    return result


def process_email_batch(messages: List[Communication]):
    now = timezone.now()
    server = get_available_smtp_server()
    
    if not server:
        Communication.objects.filter(id__in=[m.id for m in messages]).update(
            status='failed',
            error_message='No available SMTP servers',
            updated_at=now
        )
        return
    
    connection = get_connection(
        host=server.host,
        port=server.port,
        username=server.username,
        password=server.password,
        use_tls=server.use_tls
    )
    
    email_messages = []
    for message in messages:
        email = EmailMessage(
            subject=message.subject,
            body=message.content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[message.recipient],
            connection=connection,
        )
        email_messages.append(email)
    
    try:
        connection.send_messages(email_messages)
        
        Communication.objects.filter(id__in=[m.id for m in messages]).update(
            status='sent',
            sent_at=now,
            updated_at=now
        )
        
        server.messages_sent_today = F('messages_sent_today') + len(messages)
        server.save()
        
    except Exception as e:
        Communication.objects.filter(id__in=[m.id for m in messages]).update(
            status='failed',
            error_message=str(e),
            updated_at=now
        )
    finally:
        connection.close()


def process_whatsapp_batch(messages: List[Communication]):
    now = timezone.now()
    account = get_available_whatsapp_account()
    
    if not account:
        Communication.objects.filter(id__in=[m.id for m in messages]).update(
            status='failed',
            error_message='No available WhatsApp accounts',
            updated_at=now
        )
        return
    
    url = f"https://graph.facebook.com/v21.0/{account.phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {account.access_token}",
        "Content-Type": "application/json",
    }
    
    success_ids = []
    failed_messages = {}
    
    for message in messages:
        try:
            data = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": message.recipient,
                "type": "text",
                "text": {"body": message.content}
            }
            
            response = requests.post(url, headers=headers, json=data)
            response_data = response.json()
            
            if response.status_code in [200, 201] and "messages" in response_data:
                success_ids.append(message.id)
            else:
                failed_messages[message.id] = f"API Error: {response.text}"
                
        except Exception as e:
            failed_messages[message.id] = str(e)
    
    if success_ids:
        Communication.objects.filter(id__in=success_ids).update(
            status='sent',
            sent_at=now,
            updated_at=now
        )
        
        account.messages_sent_today = F('messages_sent_today') + len(success_ids)
        account.save()
    
    if failed_messages:
        for message_id, error in failed_messages.items():
            Communication.objects.filter(id=message_id).update(
                status='failed',
                error_message=error,
                updated_at=now
            )


def process_message_queue():
    now = timezone.now()
    
    with transaction.atomic():
        messages = Communication.objects.select_related(
            'messagequeue',
            'smtp_server',
            'whatsapp_account'
        ).filter(
            status='queued',
            messagequeue__scheduled_time__lte=now,
            messagequeue__locked_at__isnull=True,
            messagequeue__attempts__lt=F('messagequeue__max_attempts')
        ).order_by(
            'messagequeue__priority',
            'messagequeue__scheduled_time'
        )[:BATCH_SIZE]
        
        message_ids = [m.id for m in messages]
        if message_ids:
            Communication.objects.filter(id__in=message_ids).update(
                status='processing'
            )
    
    email_messages = []
    whatsapp_messages = []
    
    for message in messages:
        if message.type == Communication.EMAIL:
            email_messages.append(message)
        else:
            whatsapp_messages.append(message)
    
    if email_messages:
        process_email_batch(email_messages)
    
    if whatsapp_messages:
        process_whatsapp_batch(whatsapp_messages)