from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import permission_classes
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from .tasks import send_email_async, send_whatsapp_async
from .models import Communication
from .serializers import (
    EmailMessageSerializer, 
    WhatsAppMessageSerializer,
    CommunicationHistorySerializer
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
        
        queryset = Communication.objects.filter(user=request.user)
        
        if message_type in [Communication.EMAIL, Communication.WHATSAPP]:
            queryset = queryset.filter(type=message_type)
            
        queryset = queryset.order_by('-created_at')
        
        paginator = self.pagination_class()
        paginator.request = request
        page = paginator.paginate_queryset(queryset, request, view=self)
        
        serializer = CommunicationHistorySerializer(page, many=True)
        
        return paginator.get_paginated_response(serializer.data)


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


