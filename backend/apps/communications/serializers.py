from rest_framework import serializers
from .models import Communication


class CommunicationSerializer(serializers.ModelSerializer):

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

    to = serializers.CharField(max_length=20)
    message = serializers.CharField()

    def validate_to(self, value):

        if not value.startswith("+"):
            raise serializers.ValidationError(
                "Phone number must start with + and country code"
            )
        return value


class EmailMessageSerializer(serializers.Serializer):

    to = serializers.EmailField()
    subject = serializers.CharField(max_length=255)
    message = serializers.CharField()
