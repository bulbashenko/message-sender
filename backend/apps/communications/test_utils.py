from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.conf import settings
from unittest.mock import patch, MagicMock
from datetime import timedelta
from .models import (
    SMTPServer,
    WhatsAppAccount,
    Communication,
    MessageQueue
)
from .utils import (
    get_available_smtp_server,
    get_available_whatsapp_account,
    send_whatsapp_message,
    send_email_message,
    process_email_batch,
    process_whatsapp_batch,
    process_message_queue
)

User = get_user_model()

class SMTPServerUtilsTests(TestCase):
    def setUp(self):
        self.server1 = SMTPServer.objects.create(
            name='Server 1',
            host='smtp1.test.com',
            port=587,
            username='test1@test.com',
            password='pass1',
            daily_limit=100,
            messages_sent_today=50
        )
        self.server2 = SMTPServer.objects.create(
            name='Server 2',
            host='smtp2.test.com',
            port=587,
            username='test2@test.com',
            password='pass2',
            daily_limit=100,
            messages_sent_today=90
        )
        self.inactive_server = SMTPServer.objects.create(
            name='Inactive Server',
            host='smtp3.test.com',
            port=587,
            username='test3@test.com',
            password='pass3',
            is_active=False
        )

    def test_get_available_smtp_server(self):
        # Should return server with lowest messages_sent_today
        server = get_available_smtp_server()
        self.assertEqual(server, self.server1)

    def test_get_available_smtp_server_daily_reset(self):
        # Set last_reset_date to yesterday
        yesterday = timezone.now().date() - timedelta(days=1)
        self.server1.last_reset_date = yesterday
        self.server1.messages_sent_today = 100
        self.server1.save()

        server = get_available_smtp_server()
        self.assertEqual(server, self.server1)
        self.server1.refresh_from_db()
        self.assertEqual(self.server1.messages_sent_today, 0)
        self.assertEqual(self.server1.last_reset_date, timezone.now().date())

    @patch('django.core.mail.get_connection')
    def test_send_email_message(self, mock_get_connection):
        mock_connection = MagicMock()
        mock_get_connection.return_value = mock_connection
        
        user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        
        result = send_email_message(
            'recipient@test.com',
            'Test Subject',
            'Test Message',
            user
        )
        
        self.assertEqual(result['status'], 'sent')
        self.assertEqual(result['server'], self.server1.id)
        
        # Verify server count increased
        self.server1.refresh_from_db()
        self.assertEqual(self.server1.messages_sent_today, 51)

class WhatsAppUtilsTests(TestCase):
    def setUp(self):
        self.account1 = WhatsAppAccount.objects.create(
            name='Account 1',
            phone_number_id='123456789',
            access_token='token1',
            daily_limit=100,
            messages_sent_today=50
        )
        self.account2 = WhatsAppAccount.objects.create(
            name='Account 2',
            phone_number_id='987654321',
            access_token='token2',
            daily_limit=100,
            messages_sent_today=90
        )
        self.inactive_account = WhatsAppAccount.objects.create(
            name='Inactive Account',
            phone_number_id='555555555',
            access_token='token3',
            is_active=False
        )

    def test_get_available_whatsapp_account(self):
        # Should return account with lowest messages_sent_today
        account = get_available_whatsapp_account()
        self.assertEqual(account, self.account1)

    def test_get_available_whatsapp_account_daily_reset(self):
        # Set last_reset_date to yesterday
        yesterday = timezone.now().date() - timedelta(days=1)
        self.account1.last_reset_date = yesterday
        self.account1.messages_sent_today = 100
        self.account1.save()

        account = get_available_whatsapp_account()
        self.assertEqual(account, self.account1)
        self.account1.refresh_from_db()
        self.assertEqual(self.account1.messages_sent_today, 0)
        self.assertEqual(self.account1.last_reset_date, timezone.now().date())

    @patch('requests.post')
    def test_send_whatsapp_message(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "messages": [{"id": "test_message_id"}]
        }
        mock_post.return_value = mock_response
        
        user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        
        result = send_whatsapp_message(
            '+1234567890',
            'Test Message',
            'text',
            user
        )
        
        self.assertEqual(result['status'], 'sent')
        self.assertEqual(result['whatsapp_message_id'], 'test_message_id')
        
        # Verify account count increased
        self.account1.refresh_from_db()
        self.assertEqual(self.account1.messages_sent_today, 51)

class BatchProcessingTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        self.smtp_server = SMTPServer.objects.create(
            name='Test SMTP',
            host='smtp.test.com',
            port=587,
            username='test@test.com',
            password='testpass',
            daily_limit=100
        )
        self.whatsapp_account = WhatsAppAccount.objects.create(
            name='Test WhatsApp',
            phone_number_id='123456789',
            access_token='test_token',
            daily_limit=100
        )
        
        # Create test messages
        self.email_messages = []
        self.whatsapp_messages = []
        
        for i in range(3):
            email_comm = Communication.objects.create(
                user=self.user,
                type=Communication.EMAIL,
                recipient=f'test{i}@test.com',
                subject=f'Test Subject {i}',
                content=f'Test Content {i}',
                status='queued'
            )
            self.email_messages.append(email_comm)
            
            whatsapp_comm = Communication.objects.create(
                user=self.user,
                type=Communication.WHATSAPP,
                recipient=f'+123456789{i}',
                content=f'Test Content {i}',
                status='queued'
            )
            self.whatsapp_messages.append(whatsapp_comm)

    @patch('django.core.mail.get_connection')
    def test_process_email_batch(self, mock_get_connection):
        mock_connection = MagicMock()
        mock_get_connection.return_value = mock_connection
        
        process_email_batch(self.email_messages)
        
        # Verify all messages were marked as sent
        for message in self.email_messages:
            message.refresh_from_db()
            self.assertEqual(message.status, 'sent')
            self.assertIsNotNone(message.sent_at)
        
        # Verify server count increased
        self.smtp_server.refresh_from_db()
        self.assertEqual(self.smtp_server.messages_sent_today, 3)

    @patch('requests.post')
    def test_process_whatsapp_batch(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "messages": [{"id": "test_message_id"}]
        }
        mock_post.return_value = mock_response
        
        process_whatsapp_batch(self.whatsapp_messages)
        
        # Verify all messages were marked as sent
        for message in self.whatsapp_messages:
            message.refresh_from_db()
            self.assertEqual(message.status, 'sent')
            self.assertIsNotNone(message.sent_at)
        
        # Verify account count increased
        self.whatsapp_account.refresh_from_db()
        self.assertEqual(self.whatsapp_account.messages_sent_today, 3)

    @patch('apps.communications.utils.process_email_batch')
    @patch('apps.communications.utils.process_whatsapp_batch')
    def test_process_message_queue(self, mock_whatsapp_batch, mock_email_batch):
        # Create message queues
        for message in self.email_messages + self.whatsapp_messages:
            MessageQueue.objects.create(
                communication=message,
                scheduled_time=timezone.now(),
                priority=1
            )
        
        process_message_queue()
        
        # Verify batch processing was called
        mock_email_batch.assert_called_once()
        mock_whatsapp_batch.assert_called_once()
        
        # Verify messages were processed
        self.assertEqual(
            mock_email_batch.call_args[0][0],
            self.email_messages
        )
        self.assertEqual(
            mock_whatsapp_batch.call_args[0][0],
            self.whatsapp_messages
        )