from django.db import models
from django.conf import settings


class Communication(models.Model):

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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True, null=True)
    whatsapp_message_id = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        app_label = "communications"
        ordering = ["-created_at"]

    def __str__(self):
        if self.type == "email":
            return f"Email to {self.recipient} - {self.subject} ({self.status})"
        return f"WhatsApp to {self.recipient} ({self.status})"
