from django.db import models
from django.conf import settings
from django.utils import timezone


class Communication(models.Model):
    """
    Temporary storage for message delivery tracking.
    Records are meant to be short-lived and deleted after message delivery/failure.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='communications'
    )
    # Communication type constants
    EMAIL = "email"
    WHATSAPP = "whatsapp"

    TYPE_CHOICES = [
        ("email", "Email"),
        ("whatsapp", "WhatsApp"),
    ]
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("sent", "Sent"),
        ("failed", "Failed"),
    ]

    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default="email")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    recipient = models.CharField(max_length=255)
    content = models.TextField()
    subject = models.CharField(max_length=255, blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)
    whatsapp_message_id = models.CharField(max_length=100, blank=True, null=True)
    
    # Timestamp fields for tracking message lifecycle
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = "communications"

    def __str__(self):
        if self.type == "email":
            return f"Email to {self.recipient} ({self.status})"
        return f"WhatsApp to {self.recipient} ({self.status})"
