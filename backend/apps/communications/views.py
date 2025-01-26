import tweepy
import requests
from rest_framework import status, permissions, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import permission_classes, action
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from django.utils import timezone
from django.core.cache import cache
from datetime import timedelta

CACHE_TTL = 300
from .tasks import (
    send_email_async,
    send_whatsapp_async,
    search_business,
    verify_social_profiles,
    sync_google_contacts,
    bulk_message_send,
    process_message_queue_task
)
from .models import (
    Communication,
    Business,
    SocialMediaProfile,
    SMTPServer,
    WhatsAppAccount,
    MessageQueue,
    SocialAPIConfig
)
from .serializers import (
    EmailMessageSerializer, 
    WhatsAppMessageSerializer,
    CommunicationHistorySerializer,
    BusinessSerializer,
    SocialMediaProfileSerializer,
    SMTPServerSerializer,
    WhatsAppAccountSerializer,
    MessageQueueSerializer,
    SocialAPIConfigSerializer
)
from .throttles import EmailRateThrottle, WhatsAppRateThrottle


class MessageHistoryPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class MessageHistoryView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = MessageHistoryPagination
    
    def get(self, request):
        message_type = request.query_params.get('type')
        page = request.query_params.get('page', 1)
        
        cache_key = f'message_history_{request.user.id}_{message_type}_{page}'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return Response(cached_data)
        
        queryset = Communication.objects.select_related(
            'smtp_server',
            'whatsapp_account'
        ).filter(user=request.user)
        
        if message_type in [Communication.EMAIL, Communication.WHATSAPP]:
            queryset = queryset.filter(type=message_type)
            
        queryset = queryset.order_by('-created_at')
        
        paginator = self.pagination_class()
        paginator.request = request
        page = paginator.paginate_queryset(queryset, request, view=self)
        
        serializer = CommunicationHistorySerializer(page, many=True)
        response_data = paginator.get_paginated_response(serializer.data).data
        
        cache.set(cache_key, response_data, 300)
        
        return Response(response_data)


class BusinessViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BusinessSerializer
    queryset = Business.objects.prefetch_related('social_profiles').all()

    def get_queryset(self):
        queryset = super().get_queryset()
        
        if self.action == 'list':
            cache_key = f'business_list_{self.request.user.id}'
            cached_data = cache.get(cache_key)
            
            if cached_data is None:
                cached_data = list(queryset)
                cache.set(cache_key, cached_data, CACHE_TTL)
            
            return cached_data
        
        return queryset

    @action(detail=False, methods=['post'])
    def search(self, request):
        query = request.data.get('query')
        location = request.data.get('location')
        
        if not query or not location:
            return Response(
                {"error": "Both query and location are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        cache_key = f'business_search_{query}_{location}'
        cached_result = cache.get(cache_key)
        
        if cached_result:
            return Response(cached_result)
        
        task = search_business.delay(query, location)
        
        response_data = {
            "message": "Business search initiated",
            "task_id": task.id
        }
        
        cache.set(cache_key, response_data, 300)
        
        return Response(response_data, status=status.HTTP_202_ACCEPTED)

    @action(detail=True, methods=['post'])
    def verify_social_profiles(self, request, pk=None):
        business = self.get_object()
        task = verify_social_profiles.delay(business.id)
        
        return Response({
            "message": "Social profile verification initiated",
            "task_id": task.id
        }, status=status.HTTP_202_ACCEPTED)

    @action(detail=True, methods=['post'])
    def sync_to_contacts(self, request, pk=None):
        business = self.get_object()
        task = sync_google_contacts.delay(business.id)
        
        return Response({
            "message": "Google Contacts sync initiated",
            "task_id": task.id
        }, status=status.HTTP_202_ACCEPTED)


class SocialMediaProfileViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SocialMediaProfileSerializer
    queryset = SocialMediaProfile.objects.all()

    def get_queryset(self):
        return self.queryset.filter(
            business_id=self.kwargs.get('business_pk')
        )


class SMTPServerViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = SMTPServerSerializer
    queryset = SMTPServer.objects.all()

    @action(detail=True, methods=['post'])
    def reset_counter(self, request, pk=None):
        server = self.get_object()
        server.messages_sent_today = 0
        server.last_reset_date = timezone.now().date()
        server.save()
        
        return Response({
            "message": "Counter reset successfully"
        })


class WhatsAppAccountViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = WhatsAppAccountSerializer
    queryset = WhatsAppAccount.objects.all()

    @action(detail=True, methods=['post'])
    def reset_counter(self, request, pk=None):
        account = self.get_object()
        account.messages_sent_today = 0
        account.last_reset_date = timezone.now().date()
        account.save()
        
        return Response({
            "message": "Counter reset successfully"
        })


@permission_classes([permissions.IsAuthenticated])
class WhatsAppView(APIView):
    throttle_classes = [WhatsAppRateThrottle]
    
    def post(self, request):
        serializer = WhatsAppMessageSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"success": False, "error": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        comm = Communication.objects.create(
            user=request.user,
            type=Communication.WHATSAPP,
            status="pending",
            recipient=serializer.validated_data["to"],
            content=serializer.validated_data.get("message", "hello_world template")
        )
        
        task_kwargs = {
            'to_number': serializer.validated_data["to"],
            'message_type': serializer.validated_data["message_type"],
            'user_id': request.user.id,
            'comm_id': comm.id
        }
        
        if serializer.validated_data["message_type"] == "text":
            task_kwargs['message'] = serializer.validated_data["message"]
        
        task = send_whatsapp_async.apply_async(kwargs=task_kwargs)

        return Response(
            {
                "success": True,
                "data": {
                    "message": "WhatsApp message queued for delivery",
                    "task_id": task.id,
                },
            },
            status=status.HTTP_202_ACCEPTED,
        )


@permission_classes([permissions.IsAuthenticated])
class EmailView(APIView):
    throttle_classes = [EmailRateThrottle]
    
    def post(self, request):
        serializer = EmailMessageSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"success": False, "error": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        comm = Communication.objects.create(
            user=request.user,
            type=Communication.EMAIL,
            status="pending",
            recipient=serializer.validated_data["to"],
            subject=serializer.validated_data["subject"],
            content=serializer.validated_data["message"]
        )
        
        task = send_email_async.apply_async(kwargs={
            'to_email': serializer.validated_data["to"],
            'subject': serializer.validated_data["subject"],
            'message': serializer.validated_data["message"],
            'user_id': request.user.id,
            'comm_id': comm.id
        })

        return Response(
            {
                "success": True,
                "data": {
                    "message": "Email queued for delivery",
                    "task_id": task.id,
                },
            },
            status=status.HTTP_202_ACCEPTED,
        )


class BulkMessageView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        message_type = request.data.get('type')
        recipients = request.data.get('recipients', [])
        content = request.data.get('content')
        subject = request.data.get('subject')
        
        if not all([message_type, recipients, content]):
            return Response({
                "error": "type, recipients, and content are required"
            }, status=status.HTTP_400_BAD_REQUEST)
            
        if not isinstance(recipients, list):
            return Response({
                "error": "recipients must be a list"
            }, status=status.HTTP_400_BAD_REQUEST)
            
        if message_type not in [Communication.EMAIL, Communication.WHATSAPP]:
            return Response({
                "error": "Invalid message type"
            }, status=status.HTTP_400_BAD_REQUEST)
            
        task = bulk_message_send.delay(
            message_type=message_type,
            recipients=recipients,
            content=content,
            subject=subject,
            user_id=request.user.id
        )
        
        return Response({
            "message": f"Bulk {message_type} send initiated",
            "task_id": task.id,
            "recipient_count": len(recipients)
        }, status=status.HTTP_202_ACCEPTED)


class SocialAPIConfigViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = SocialAPIConfigSerializer
    queryset = SocialAPIConfig.objects.all()

    @action(detail=True, methods=['post'])
    def verify_credentials(self, request, pk=None):
        config = self.get_object()
        try:
            if config.platform == 'twitter':
                auth = tweepy.OAuthHandler(config.api_key, config.api_secret)
                auth.set_access_token(config.access_token, config.token_secret)
                api = tweepy.API(auth)
                api.verify_credentials()
            elif config.platform == 'linkedin':
                headers = {'Authorization': f'Bearer {config.access_token}'}
                response = requests.get('https://api.linkedin.com/v2/me', headers=headers)
                response.raise_for_status()
            
            return Response({
                "status": "success",
                "message": f"{config.platform} credentials verified successfully"
            })
            
        except Exception as e:
            return Response({
                "status": "error",
                "error": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class MessageQueueView(APIView):
    permission_classes = [permissions.IsAdminUser]
    
    def get(self, request):
        status_filter = request.query_params.get('status', 'queued')
        message_type = request.query_params.get('type')
        
        cache_key = f'message_queue_{status_filter}_{message_type}'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return Response(cached_data)
        
        queryset = MessageQueue.objects.filter(
            communication__status=status_filter
        ).select_related(
            'communication',
            'communication__user',
            'smtp_server',
            'whatsapp_account'
        )
        
        if message_type:
            queryset = queryset.filter(communication__type=message_type)
        
        serializer = MessageQueueSerializer(queryset, many=True)
        response_data = serializer.data
        
        cache.set(cache_key, response_data, 60)
        
        return Response(response_data)

    def post(self, request):
        action = request.data.get('action', 'process')
        
        if action == 'process':
            task = process_message_queue_task.delay()
            message = "Queue processing initiated"
        elif action == 'clear':
            MessageQueue.objects.filter(
                locked_at__lt=timezone.now() - timedelta(minutes=30)
            ).update(locked_at=None, locked_by=None)
            message = "Cleared stuck messages"
        else:
            return Response({
                "error": "Invalid action"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            "message": message,
            "task_id": task.id if action == 'process' else None
        }, status=status.HTTP_202_ACCEPTED)