from rest_framework import serializers
from django.core.validators import URLValidator
from django.utils import timezone
from .models import (
    Communication,
    Business,
    SocialMediaProfile,
    SMTPServer,
    WhatsAppAccount,
    MessageQueue,
    SocialAPIConfig
)


class CommunicationHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Communication
        fields = [
            'id', 'type', 'status', 'recipient', 'content', 'subject',
            'error_message', 'whatsapp_message_id', 'created_at',
            'sent_at'
        ]
        read_only_fields = fields


class WhatsAppMessageSerializer(serializers.Serializer):
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
    to = serializers.EmailField()
    subject = serializers.CharField(max_length=255)
    message = serializers.CharField()


class SocialMediaProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialMediaProfile
        fields = [
            'id', 'business', 'platform', 'profile_url', 'verified',
            'verification_date', 'profile_data', 'created_at', 'updated_at'
        ]
        read_only_fields = ['verified', 'verification_date', 'profile_data', 'created_at', 'updated_at']

    def validate_profile_url(self, value):
        validator = URLValidator()
        try:
            validator(value)
        except:
            raise serializers.ValidationError("Invalid URL format")
        return value


class BusinessSerializer(serializers.ModelSerializer):
    social_profiles = SocialMediaProfileSerializer(many=True, read_only=True)
    
    class Meta:
        model = Business
        fields = [
            'id', 'name', 'address', 'phone_number', 'website',
            'category', 'google_maps_link', 'google_place_id',
            'social_profiles', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate_phone_number(self, value):
        if not value.startswith("+"):
            raise serializers.ValidationError(
                "Phone number must start with + and country code"
            )
        return value

    def validate_website(self, value):
        if value:
            validator = URLValidator()
            try:
                validator(value)
            except:
                raise serializers.ValidationError("Invalid URL format")
        return value

    def validate_google_maps_link(self, value):
        validator = URLValidator()
        try:
            validator(value)
        except:
            raise serializers.ValidationError("Invalid Google Maps URL format")
        return value


class SMTPServerSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    
    class Meta:
        model = SMTPServer
        fields = [
            'id', 'name', 'host', 'port', 'username', 'password',
            'use_tls', 'is_active', 'daily_limit', 'messages_sent_today',
            'last_reset_date'
        ]
        read_only_fields = ['messages_sent_today', 'last_reset_date']

    def validate_port(self, value):
        if not (0 <= value <= 65535):
            raise serializers.ValidationError("Invalid port number")
        return value

    def validate_daily_limit(self, value):
        if value < 0:
            raise serializers.ValidationError("Daily limit cannot be negative")
        return value


class WhatsAppAccountSerializer(serializers.ModelSerializer):
    access_token = serializers.CharField(write_only=True, style={'input_type': 'password'})
    
    class Meta:
        model = WhatsAppAccount
        fields = [
            'id', 'name', 'phone_number_id', 'access_token',
            'is_active', 'daily_limit', 'messages_sent_today',
            'last_reset_date'
        ]
        read_only_fields = ['messages_sent_today', 'last_reset_date']

    def validate_daily_limit(self, value):
        if value < 0:
            raise serializers.ValidationError("Daily limit cannot be negative")
        return value


class SocialAPIConfigSerializer(serializers.ModelSerializer):
    api_key = serializers.CharField(write_only=True, style={'input_type': 'password'})
    api_secret = serializers.CharField(write_only=True, style={'input_type': 'password'})
    access_token = serializers.CharField(write_only=True, style={'input_type': 'password'}, required=False)
    token_secret = serializers.CharField(write_only=True, style={'input_type': 'password'}, required=False)
    
    class Meta:
        model = SocialAPIConfig
        fields = [
            'id', 'platform', 'api_key', 'api_secret',
            'access_token', 'token_secret', 'daily_request_limit',
            'requests_made_today', 'last_reset_date'
        ]
        read_only_fields = ['requests_made_today', 'last_reset_date']

    def validate_daily_request_limit(self, value):
        if value < 0:
            raise serializers.ValidationError("Daily limit cannot be negative")
        return value


class BulkMessageSerializer(serializers.Serializer):
    type = serializers.ChoiceField(choices=['email', 'whatsapp'])
    recipients = serializers.ListField(
        child=serializers.CharField(),
        min_length=1,
        max_length=1000
    )
    content = serializers.CharField()
    subject = serializers.CharField(required=False)

    def validate_recipients(self, value):
        if len(value) > 1000:
            raise serializers.ValidationError(
                "Maximum 1000 recipients allowed per bulk operation"
            )
        
        message_type = self.initial_data.get('type')
        if message_type == 'email':
            email_validator = EmailValidator()
            for recipient in value:
                try:
                    email_validator(recipient)
                except ValidationError:
                    raise serializers.ValidationError(
                        f"Invalid email format: {recipient}"
                    )
        elif message_type == 'whatsapp':
            for recipient in value:
                if not recipient.startswith('+'):
                    raise serializers.ValidationError(
                        f"WhatsApp number must start with +: {recipient}"
                    )
        
        return value

    def validate(self, data):
        if data['type'] == 'email' and not data.get('subject'):
            raise serializers.ValidationError({
                'subject': 'Subject is required for email messages'
            })
        return data


class MessageQueueSerializer(serializers.ModelSerializer):
    communication_details = CommunicationHistorySerializer(source='communication', read_only=True)
    
    class Meta:
        model = MessageQueue
        fields = [
            'id', 'communication', 'communication_details',
            'priority', 'scheduled_time', 'attempts', 'max_attempts',
            'smtp_server', 'whatsapp_account', 'locked_at', 'locked_by'
        ]
        read_only_fields = ['locked_at', 'locked_by', 'attempts']

    def validate_max_attempts(self, value):
        if value < 1:
            raise serializers.ValidationError("Maximum attempts must be at least 1")
        return value

    def validate_priority(self, value):
        if value < 0:
            raise serializers.ValidationError("Priority cannot be negative")
        return value

    def validate_scheduled_time(self, value):
        if value < timezone.now():
            raise serializers.ValidationError("Scheduled time cannot be in the past")
        return value