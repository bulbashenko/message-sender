import os
import logging
from typing import Dict, Any, List, Optional
from django.utils import timezone
from django.conf import settings
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from bs4 import BeautifulSoup
import requests
import asyncio
import aiohttp

from config.celery import app
from .models import (
    Communication,
    Business,
    SocialMediaProfile,
    MessageQueue
)
from .utils import (
    send_email_message,
    send_whatsapp_message,
    process_message_queue
)

logger = logging.getLogger(__name__)


@app.task(name='communications.process_message_queue_task')
def process_message_queue_task():
    try:
        process_message_queue()
    except Exception as e:
        logger.error(f"Error processing message queue: {str(e)}")


@app.task(name='communications.send_email_async', bind=True)
def send_email_async(self, to_email: str, subject: str, message: str, user_id: int, comm_id: int):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    user = User.objects.get(id=user_id)
    comm = Communication.objects.get(id=comm_id)

    try:
        MessageQueue.objects.get_or_create(
            communication=comm,
            defaults={
                'scheduled_time': timezone.now(),
                'priority': 1
            }
        )
        comm.status = "queued"
        comm.save()

        return {
            "status": "queued",
            "recipient": to_email
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
        MessageQueue.objects.get_or_create(
            communication=comm,
            defaults={
                'scheduled_time': timezone.now(),
                'priority': 1
            }
        )
        comm.status = "queued"
        comm.save()

        return {
            "status": "queued",
            "recipient": to_number
        }
    except Exception as e:
        comm.status = "failed"
        comm.error_message = str(e)
        comm.save()
        return {"status": "error", "error": str(e), "recipient": to_number}


@app.task(name='communications.search_business', bind=True)
def search_business(self, query: str, location: str) -> Dict[str, Any]:
    try:
        credentials = Credentials.from_authorized_user_info(
            settings.GOOGLE_CREDENTIALS
        )
        places_service = build('places', 'v1', credentials=credentials)
        
        search_request = {
            'textQuery': f"{query} in {location}",
            'locationBias': {'ipBias': {}},
            'fields': [
                'name',
                'formattedAddress',
                'phoneNumber',
                'websiteUri',
                'types',
                'googleMapsUri',
                'placeId'
            ]
        }
        
        response = places_service.places().searchText(body=search_request).execute()
        
        businesses = []
        for place in response.get('places', []):
            business_data = {
                'name': place.get('name'),
                'address': place.get('formattedAddress'),
                'phone_number': place.get('phoneNumber', ''),
                'website': place.get('websiteUri', ''),
                'category': ', '.join(place.get('types', [])),
                'google_maps_link': place.get('googleMapsUri', ''),
                'google_place_id': place.get('placeId')
            }
            
            business, created = Business.objects.update_or_create(
                google_place_id=business_data['google_place_id'],
                defaults=business_data
            )
            
            businesses.append(business_data)
        
        return {
            "status": "success",
            "businesses": businesses
        }
        
    except Exception as e:
        logger.error(f"Error searching businesses: {str(e)}")
        return {
            "status": "error",
            "error": str(e)
        }


async def verify_social_profile(session: aiohttp.ClientSession, url: str) -> Dict[str, Any]:
    try:
        async with session.get(url) as response:
            if response.status == 200:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                title = soup.title.string if soup.title else ""
                meta_desc = soup.find('meta', {'name': 'description'})
                description = meta_desc.get('content', '') if meta_desc else ""
                
                return {
                    "exists": True,
                    "title": title,
                    "description": description,
                    "status_code": response.status
                }
            return {
                "exists": False,
                "status_code": response.status
            }
    except Exception as e:
        return {
            "exists": False,
            "error": str(e)
        }


@app.task(name='communications.verify_social_profiles', bind=True)
def verify_social_profiles(self, business_id: int):
    try:
        business = Business.objects.get(id=business_id)
        profiles = SocialMediaProfile.objects.filter(business=business, verified=False)
        
        async def verify_all_profiles():
            async with aiohttp.ClientSession() as session:
                tasks = [
                    verify_social_profile(session, profile.profile_url)
                    for profile in profiles
                ]
                results = await asyncio.gather(*tasks)
                return results
        
        loop = asyncio.get_event_loop()
        results = loop.run_until_complete(verify_all_profiles())
        
        for profile, result in zip(profiles, results):
            profile.verified = result.get('exists', False)
            profile.verification_date = timezone.now() if result.get('exists') else None
            profile.profile_data = result
            profile.save()
        
        return {
            "status": "success",
            "verified_count": sum(1 for r in results if r.get('exists', False))
        }
        
    except Exception as e:
        logger.error(f"Error verifying social profiles: {str(e)}")
        return {
            "status": "error",
            "error": str(e)
        }


@app.task(name='communications.sync_google_contacts', bind=True)
def sync_google_contacts(self, business_id: int):
    try:
        business = Business.objects.get(id=business_id)
        credentials = Credentials.from_authorized_user_info(
            settings.GOOGLE_CREDENTIALS
        )
        
        service = build('people', 'v1', credentials=credentials)
        
        query = f"name:{business.name} OR phoneNumber:{business.phone_number}"
        existing = service.people().searchContacts(
            query=query,
            readMask='names,phoneNumbers,addresses,urls'
        ).execute()
        
        contact_data = {
            'names': [{'givenName': business.name}],
            'phoneNumbers': [{'value': business.phone_number}],
            'addresses': [{'formattedValue': business.address}],
            'urls': []
        }
        
        if business.website:
            contact_data['urls'].append({
                'value': business.website,
                'type': 'website'
            })
        
        if business.google_maps_link:
            contact_data['urls'].append({
                'value': business.google_maps_link,
                'type': 'map'
            })
        
        for profile in business.social_profiles.filter(verified=True):
            contact_data['urls'].append({
                'value': profile.profile_url,
                'type': profile.platform
            })
        
        if existing.get('results'):
            contact = existing['results'][0]
            result = service.people().updateContact(
                resourceName=contact['person']['resourceName'],
                body=contact_data,
                updatePersonFields='names,phoneNumbers,addresses,urls'
            ).execute()
        else:
            result = service.people().createContact(
                body=contact_data
            ).execute()
        
        return {
            "status": "success",
            "contact_id": result.get('resourceName'),
            "action": "updated" if existing.get('results') else "created"
        }
        
    except Exception as e:
        logger.error(f"Error syncing to Google Contacts: {str(e)}")
        return {
            "status": "error",
            "error": str(e)
        }


@app.task(name='communications.bulk_message_send', bind=True)
def bulk_message_send(self, message_type: str, recipients: List[str], content: str, subject: str = None, user_id: int = None):
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.get(id=user_id) if user_id else None
        
        communications = []
        base_priority = 5
        
        for recipient in recipients:
            comm = Communication.objects.create(
                user=user,
                type=message_type,
                status="pending",
                recipient=recipient,
                content=content,
                subject=subject
            )
            communications.append(comm)
            
            MessageQueue.objects.create(
                communication=comm,
                priority=base_priority,
                scheduled_time=timezone.now() + timedelta(
                    seconds=len(communications) * 2 
                )
            )
        
        process_message_queue_task.delay()
        
        return {
            "status": "success",
            "queued_count": len(communications)
        }
        
    except Exception as e:
        logger.error(f"Error in bulk message send: {str(e)}")
        return {
            "status": "error",
            "error": str(e)
        }