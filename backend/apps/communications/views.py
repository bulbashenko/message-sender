from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from .tasks import send_email_async
from .models import Communication
from .serializers import CommunicationSerializer, EmailMessageSerializer
from rest_framework.decorators import permission_classes


@permission_classes([permissions.IsAuthenticated])
class EmailView(APIView):
    """
    Send and retrieve emails
    """

    def post(self, request):
        serializer = EmailMessageSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"success": False, "error": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Queue the email
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
        """Get all email communications"""
        communications = Communication.objects.filter(
            channel=Communication.EMAIL
        ).order_by("-created_at")[:10]

        serializer = CommunicationSerializer(communications, many=True)
        return Response({"success": True, "data": serializer.data})
