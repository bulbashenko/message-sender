from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import permission_classes
from .tasks import send_email_async, send_whatsapp_async
from .serializers import EmailMessageSerializer, WhatsAppMessageSerializer


@permission_classes([permissions.IsAuthenticated])
class WhatsAppView(APIView):
    """
    API endpoint for sending WhatsApp messages.
    Messages are processed asynchronously with no history maintained.
    """
    def post(self, request):
        serializer = WhatsAppMessageSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"success": False, "error": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        # Start async task immediately with explicit kwargs
        task = send_whatsapp_async.apply_async(kwargs={
            'to_number': serializer.validated_data["to"],
            'message': serializer.validated_data["message"],
            'user_id': request.user.id
        })

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
    """
    API endpoint for sending email messages.
    Messages are processed asynchronously with no history maintained.
    """
    def post(self, request):
        serializer = EmailMessageSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"success": False, "error": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        # Start async task immediately with explicit kwargs
        task = send_email_async.apply_async(kwargs={
            'to_email': serializer.validated_data["to"],
            'subject': serializer.validated_data["subject"],
            'message': serializer.validated_data["message"],
            'user_id': request.user.id
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


