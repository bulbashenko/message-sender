from rest_framework import serializers
from .models import Communication


class CommunicationSerializer(serializers.ModelSerializer):
    """
    Serializer for the Communication model
    """

    class Meta:
        model = Communication
        fields = [
            "id",
            "channel",
            "status",
            "recipient",
            "content",
            "subject",
            "created_at",
            "sent_at",
            "error_message",
        ]
        read_only_fields = ["id", "created_at", "sent_at", "status", "error_message"]


class WhatsAppMessageSerializer(serializers.Serializer):
    """
    Serializer for WhatsApp message requests
    """

    to = serializers.CharField(max_length=20)
    message = serializers.CharField()

    def validate_to(self, value):
        """
        Validate phone number format
        """
        if not value.startswith("+"):
            raise serializers.ValidationError(
                "Phone number must start with + and country code"
            )
        return value


class EmailMessageSerializer(serializers.Serializer):
    """
    Serializer for email message requests
    """

    to = serializers.EmailField()
    subject = serializers.CharField(max_length=255)
    message = serializers.CharField()
