from rest_framework import serializers
from .models import Communication


class CommunicationHistorySerializer(serializers.ModelSerializer):
    """
    Serializer for Communication model.
    Used for displaying message history in the dashboard.
    """
    class Meta:
        model = Communication
        fields = [
            'id', 'type', 'status', 'recipient', 'content', 'subject',
            'error_message', 'whatsapp_message_id', 'created_at',
            'sent_at'
        ]
        read_only_fields = fields


class WhatsAppMessageSerializer(serializers.Serializer):
    """
    Serializer for WhatsApp messages.
    Supports both template and regular text messages.
    """
    to = serializers.CharField(max_length=20)
    message = serializers.CharField(required=False)
    message_type = serializers.ChoiceField(choices=['template', 'text'], default='text')

    def validate(self, data):
        if data['message_type'] == 'text' and not data.get('message'):
            raise serializers.ValidationError({
                'message': 'Message is required for text message type'
            })
        return data

    def validate_to(self, value):
        if not value.startswith("+"):
            raise serializers.ValidationError(
                "Phone number must start with + and country code"
            )
        return value


class EmailMessageSerializer(serializers.Serializer):
    """
    Serializer for email messages.
    Validates message data without persisting to database.
    """
    to = serializers.EmailField()
    subject = serializers.CharField(max_length=255)
    message = serializers.CharField()
