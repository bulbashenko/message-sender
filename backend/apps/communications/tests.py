from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth import get_user_model
from datetime import timedelta
from .models import (
    Business,
    SocialMediaProfile,
    SocialAPIConfig,
    SMTPServer,
    WhatsAppAccount,
    MessageQueue,
    Communication
)

User = get_user_model()

class BusinessModelTests(TestCase):
    def setUp(self):
        self.business_data = {
            'name': 'Test Business',
            'address': '123 Test St',
            'phone_number': '+1234567890',
            'website': 'https://testbusiness.com',
            'category': 'Test Category',
            'google_maps_link': 'https://maps.google.com/test',
            'google_place_id': 'test_place_id_123'
        }

    def test_business_creation(self):
        business = Business.objects.create(**self.business_data)
        self.assertEqual(business.name, self.business_data['name'])
        self.assertEqual(business.google_place_id, self.business_data['google_place_id'])

    def test_unique_google_place_id(self):
        Business.objects.create(**self.business_data)
        with self.assertRaises(ValidationError):
            duplicate_business = Business(
                **{**self.business_data, 'name': 'Another Business'}
            )
            duplicate_business.full_clean()

class SocialMediaProfileTests(TestCase):
    def setUp(self):
        self.business = Business.objects.create(
            name='Test Business',
            address='123 Test St',
            phone_number='+1234567890',
            website='https://testbusiness.com',
            category='Test Category',
            google_maps_link='https://maps.google.com/test',
            google_place_id='test_place_id_123'
        )
        self.profile_data = {
            'business': self.business,
            'platform': 'facebook',
            'profile_url': 'https://facebook.com/testbusiness',
            'profile_id': '123456789',
            'verified': True,
            'verification_date': timezone.now(),
            'profile_data': {'followers': 1000},
            'engagement_metrics': {'facebook': {'likes': 500}}
        }

    def test_profile_creation(self):
        profile = SocialMediaProfile.objects.create(**self.profile_data)
        self.assertEqual(profile.platform, 'facebook')
        self.assertEqual(profile.get_platform_metrics(), {'likes': 500})

    def test_unique_together_constraint(self):
        SocialMediaProfile.objects.create(**self.profile_data)
        with self.assertRaises(ValidationError):
            duplicate_profile = SocialMediaProfile(
                **self.profile_data
            )
            duplicate_profile.full_clean()

class SocialAPIConfigTests(TestCase):
    def setUp(self):
        self.config = SocialAPIConfig.objects.create(
            platform='facebook',
            api_key='test_key',
            api_secret='test_secret',
            daily_request_limit=100
        )

    def test_daily_count_reset(self):
        self.config.requests_made_today = 50
        self.config.last_reset_date = timezone.now().date() - timedelta(days=1)
        self.config.save()
        
        self.config.reset_daily_count()
        self.assertEqual(self.config.requests_made_today, 0)
        self.assertEqual(self.config.last_reset_date, timezone.now().date())

class SMTPServerTests(TestCase):
    def setUp(self):
        self.smtp_server = SMTPServer.objects.create(
            name='Test SMTP',
            host='smtp.test.com',
            port=587,
            username='test@test.com',
            password='test_password',
            daily_limit=1000
        )

    def test_daily_count_reset(self):
        self.smtp_server.messages_sent_today = 500
        self.smtp_server.last_reset_date = timezone.now().date() - timedelta(days=1)
        self.smtp_server.save()
        
        self.smtp_server.reset_daily_count()
        self.assertEqual(self.smtp_server.messages_sent_today, 0)
        self.assertEqual(self.smtp_server.last_reset_date, timezone.now().date())

class WhatsAppAccountTests(TestCase):
    def setUp(self):
        self.whatsapp_account = WhatsAppAccount.objects.create(
            name='Test WhatsApp',
            phone_number_id='123456789',
            access_token='test_token',
            daily_limit=1000
        )

    def test_daily_count_reset(self):
        self.whatsapp_account.messages_sent_today = 500
        self.whatsapp_account.last_reset_date = timezone.now().date() - timedelta(days=1)
        self.whatsapp_account.save()
        
        self.whatsapp_account.reset_daily_count()
        self.assertEqual(self.whatsapp_account.messages_sent_today, 0)
        self.assertEqual(self.whatsapp_account.last_reset_date, timezone.now().date())

class MessageQueueTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        self.business = Business.objects.create(
            name='Test Business',
            address='123 Test St',
            phone_number='+1234567890',
            category='Test Category',
            google_maps_link='https://maps.google.com/test',
            google_place_id='test_place_id_123'
        )
        self.communication = Communication.objects.create(
            user=self.user,
            business=self.business,
            type=Communication.EMAIL,
            recipient='test@test.com',
            content='Test content',
            subject='Test subject'
        )

    def test_queue_creation_and_priority(self):
        queue_item = MessageQueue.objects.create(
            communication=self.communication,
            priority=1,
            scheduled_time=timezone.now()
        )
        self.assertEqual(queue_item.priority, 1)
        self.assertEqual(queue_item.attempts, 0)
        self.assertEqual(queue_item.max_attempts, 3)

    def test_queue_ordering(self):
        # Create messages with different priorities
        now = timezone.now()
        MessageQueue.objects.create(
            communication=self.communication,
            priority=2,
            scheduled_time=now
        )
        high_priority = MessageQueue.objects.create(
            communication=Communication.objects.create(
                user=self.user,
                type=Communication.EMAIL,
                recipient='test2@test.com',
                content='Test content 2'
            ),
            priority=1,
            scheduled_time=now + timedelta(minutes=5)
        )
        
        # Get first item in queue
        first_in_queue = MessageQueue.objects.all().first()
        self.assertEqual(first_in_queue, high_priority)

class CommunicationModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        self.business = Business.objects.create(
            name='Test Business',
            address='123 Test St',
            phone_number='+1234567890',
            category='Test Category',
            google_maps_link='https://maps.google.com/test',
            google_place_id='test_place_id_123'
        )

    def test_communication_creation(self):
        comm = Communication.objects.create(
            user=self.user,
            business=self.business,
            type=Communication.EMAIL,
            recipient='test@test.com',
            content='Test content',
            subject='Test subject'
        )
        self.assertEqual(comm.status, 'pending')
        self.assertEqual(str(comm), f"Email to test@test.com (pending)")

    def test_whatsapp_communication_str(self):
        comm = Communication.objects.create(
            user=self.user,
            type=Communication.WHATSAPP,
            recipient='+1234567890',
            content='Test WhatsApp message'
        )
        self.assertEqual(str(comm), f"WhatsApp to +1234567890 (pending)")

    def test_communication_status_transitions(self):
        comm = Communication.objects.create(
            user=self.user,
            type=Communication.EMAIL,
            recipient='test@test.com',
            content='Test content'
        )
        
        # Test status transitions
        self.assertEqual(comm.status, 'pending')
        
        comm.status = 'queued'
        comm.save()
        self.assertEqual(comm.status, 'queued')
        
        comm.status = 'processing'
        comm.save()
        self.assertEqual(comm.status, 'processing')
        
        comm.status = 'sent'
        comm.sent_at = timezone.now()
        comm.save()
        self.assertEqual(comm.status, 'sent')
        self.assertIsNotNone(comm.sent_at)