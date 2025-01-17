from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from .tasks import send_email_async, send_whatsapp_async
from .models import Communication
from .serializers import (
    CommunicationSerializer,
    EmailMessageSerializer,
    WhatsAppMessageSerializer,
)
from rest_framework.decorators import permission_classes


@permission_classes([permissions.IsAuthenticated])
class WhatsAppView(APIView):

    def post(self, request):
        serializer = WhatsAppMessageSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"success": False, "error": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        task = send_whatsapp_async.delay(
            serializer.validated_data["to"],
            serializer.validated_data["message"],
        )

        return Response(
            {
                "success": True,
                "data": {
                    "message": "WhatsApp message queued successfully",
                    "task_id": task.id,
                },
            },
            status=status.HTTP_202_ACCEPTED,
        )

    def get(self, request):
        communications = Communication.objects.filter(
            channel=Communication.WHATSAPP
        ).order_by("-created_at")[:10]

        serializer = CommunicationSerializer(communications, many=True)
        return Response({"success": True, "data": serializer.data})


@permission_classes([permissions.IsAuthenticated])
class EmailView(APIView):

    def post(self, request):
        serializer = EmailMessageSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"success": False, "error": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        task = send_email_async.delay(
            serializer.validated_data["to"],
            serializer.validated_data["subject"],
            serializer.validated_data["message"],
        )

        return Response(
            {
                "success": True,
                "data": {"message": "Email queued successfully", "task_id": task.id},
            },
            status=status.HTTP_202_ACCEPTED,
        )

    def get(self, request):
        communications = Communication.objects.filter(
            channel=Communication.EMAIL
        ).order_by("-created_at")[:10]

        serializer = CommunicationSerializer(communications, many=True)
        return Response({"success": True, "data": serializer.data})
