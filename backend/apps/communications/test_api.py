from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from django.utils import timezone
from unittest.mock import patch
from .models import (
    Communication,
    Business,
    SocialMediaProfile,
    SMTPServer,
    WhatsAppAccount,
    MessageQueue,
    SocialAPIConfig
)

User = get_user_model()

class BaseAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Create regular user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        # Create admin user
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='adminpass123'
        )
        # Create test business
        self.business = Business.objects.create(
            name='Test Business',
            address='123 Test St',
            phone_number='+1234567890',
            category='Test Category',
            google_maps_link='https://maps.google.com/test',
            google_place_id='test_place_id_123'
        )

class MessageHistoryTests(BaseAPITest):
    def setUp(self):
        super().setUp()
        # Create some test communications
        self.email_comm = Communication.objects.create(
            user=self.user,
            type=Communication.EMAIL,
            recipient='test@test.com',
            content='Test content',
            subject='Test subject'
        )
        self.whatsapp_comm = Communication.objects.create(
            user=self.user,
            type=Communication.WHATSAPP,
            recipient='+1234567890',
            content='Test content'
        )

    def test_message_history_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('communications:message-history'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_message_history_filtered(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(
            reverse('communications:message-history'),
            {'type': Communication.EMAIL}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_message_history_unauthorized(self):
        response = self.client.get(reverse('communications:message-history'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class BusinessViewSetTests(BaseAPITest):
    def test_business_list(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('communications:business-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    @patch('apps.communications.tasks.search_business.delay')
    def test_business_search(self, mock_task):
        self.client.force_authenticate(user=self.user)
        mock_task.return_value.id = 'test_task_id'
        
        response = self.client.post(
            reverse('communications:business-search'),
            {
                'query': 'test business',
                'location': 'test location'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(response.data['task_id'], 'test_task_id')

    @patch('apps.communications.tasks.verify_social_profiles.delay')
    def test_verify_social_profiles(self, mock_task):
        self.client.force_authenticate(user=self.user)
        mock_task.return_value.id = 'test_task_id'
        
        response = self.client.post(
            reverse('communications:business-verify-social-profiles', args=[self.business.id])
        )
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

class EmailViewTests(BaseAPITest):
    def setUp(self):
        super().setUp()
        self.valid_payload = {
            'to': 'recipient@test.com',
            'subject': 'Test Subject',
            'message': 'Test Message'
        }

    @patch('apps.communications.tasks.send_email_async.apply_async')
    def test_send_email(self, mock_task):
        self.client.force_authenticate(user=self.user)
        mock_task.return_value.id = 'test_task_id'
        
        response = self.client.post(
            reverse('communications:email-send'),
            self.valid_payload,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertTrue(response.data['success'])
        self.assertEqual(
            response.data['data']['message'],
            'Email queued for delivery'
        )

    def test_send_email_invalid_data(self):
        self.client.force_authenticate(user=self.user)
        invalid_payload = {
            'to': 'invalid-email',
            'subject': '',
            'message': ''
        }
        response = self.client.post(
            reverse('communications:email-send'),
            invalid_payload,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class WhatsAppViewTests(BaseAPITest):
    def setUp(self):
        super().setUp()
        self.valid_payload = {
            'to': '+1234567890',
            'message_type': 'text',
            'message': 'Test Message'
        }

    @patch('apps.communications.tasks.send_whatsapp_async.apply_async')
    def test_send_whatsapp(self, mock_task):
        self.client.force_authenticate(user=self.user)
        mock_task.return_value.id = 'test_task_id'
        
        response = self.client.post(
            reverse('communications:whatsapp-send'),
            self.valid_payload,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertTrue(response.data['success'])

    def test_send_whatsapp_invalid_data(self):
        self.client.force_authenticate(user=self.user)
        invalid_payload = {
            'to': 'invalid-number',
            'message_type': 'invalid',
            'message': ''
        }
        response = self.client.post(
            reverse('communications:whatsapp-send'),
            invalid_payload,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class BulkMessageViewTests(BaseAPITest):
    def setUp(self):
        super().setUp()
        self.valid_payload = {
            'type': Communication.EMAIL,
            'recipients': ['test1@test.com', 'test2@test.com'],
            'content': 'Test content',
            'subject': 'Test subject'
        }

    @patch('apps.communications.tasks.bulk_message_send.delay')
    def test_bulk_message_send(self, mock_task):
        self.client.force_authenticate(user=self.user)
        mock_task.return_value.id = 'test_task_id'
        
        response = self.client.post(
            reverse('communications:bulk-send'),
            self.valid_payload,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(response.data['recipient_count'], 2)

class AdminAPITests(BaseAPITest):
    def setUp(self):
        super().setUp()
        self.smtp_server = SMTPServer.objects.create(
            name='Test SMTP',
            host='smtp.test.com',
            port=587,
            username='test@test.com',
            password='test_password'
        )
        self.whatsapp_account = WhatsAppAccount.objects.create(
            name='Test WhatsApp',
            phone_number_id='123456789',
            access_token='test_token'
        )
        self.social_config = SocialAPIConfig.objects.create(
            platform='facebook',
            api_key='test_key',
            api_secret='test_secret'
        )

    def test_smtp_server_admin_access(self):
        # Test admin access
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(reverse('communications:smtp-server-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test regular user access denied
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('communications:smtp-server-list'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_whatsapp_account_admin_access(self):
        # Test admin access
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(reverse('communications:whatsapp-account-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test regular user access denied
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('communications:whatsapp-account-list'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch('tweepy.API')
    def test_social_api_config_verify_credentials(self, mock_api):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(
            reverse(
                'communications:social-config-verify-credentials',
                args=[self.social_config.id]
            )
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class MessageQueueViewTests(BaseAPITest):
    def setUp(self):
        super().setUp()
        self.communication = Communication.objects.create(
            user=self.user,
            type=Communication.EMAIL,
            recipient='test@test.com',
            content='Test content',
            subject='Test subject',
            status='queued'
        )
        self.queue_item = MessageQueue.objects.create(
            communication=self.communication,
            scheduled_time=timezone.now(),
            priority=1
        )

    def test_queue_list_admin_only(self):
        # Test admin access
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(reverse('communications:message-queue'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test regular user access denied
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('communications:message-queue'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch('apps.communications.tasks.process_message_queue_task.delay')
    def test_process_queue(self, mock_task):
        self.client.force_authenticate(user=self.admin_user)
        mock_task.return_value.id = 'test_task_id'
        
        response = self.client.post(
            reverse('communications:message-queue'),
            {'action': 'process'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)