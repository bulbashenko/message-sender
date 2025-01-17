from rest_framework import serializers


class WhatsAppMessageSerializer(serializers.Serializer):
    """
    Serializer for WhatsApp messages.
    Validates message data without persisting to database.
    """
    to = serializers.CharField(max_length=20)
    message = serializers.CharField()

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
