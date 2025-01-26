from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import URLValidator


class Business(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    phone_number = models.CharField(max_length=50)
    website = models.URLField(max_length=500, null=True, blank=True)
    category = models.CharField(max_length=100)
    google_maps_link = models.URLField(max_length=500)
    google_place_id = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'communications'
        verbose_name_plural = "businesses"

    def __str__(self):
        return self.name


class SocialMediaProfile(models.Model):
    PLATFORM_CHOICES = [
        ('facebook', 'Facebook'),
        ('twitter', 'Twitter'),
        ('linkedin', 'LinkedIn')
    ]
    
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='social_profiles')
    platform = models.CharField(max_length=50, choices=PLATFORM_CHOICES)
    profile_url = models.URLField(max_length=500)
    profile_id = models.CharField(max_length=255, null=True, blank=True)
    verified = models.BooleanField(default=False)
    verification_date = models.DateTimeField(null=True, blank=True)
    profile_data = models.JSONField(default=dict)
    engagement_metrics = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'communications'
        unique_together = ['business', 'platform', 'profile_url']

    def __str__(self):
        return f"{self.business.name} - {self.platform}"

    def get_platform_metrics(self):
        return self.engagement_metrics.get(self.platform, {})


class SocialAPIConfig(models.Model):
    platform = models.CharField(max_length=50, choices=SocialMediaProfile.PLATFORM_CHOICES, unique=True)
    api_key = models.CharField(max_length=500)
    api_secret = models.CharField(max_length=500)
    access_token = models.CharField(max_length=500, null=True, blank=True)
    token_secret = models.CharField(max_length=500, null=True, blank=True)
    daily_request_limit = models.IntegerField(default=1000)
    requests_made_today = models.IntegerField(default=0)
    last_reset_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.platform} API Configuration"

    def reset_daily_count(self):
        today = timezone.now().date()
        if self.last_reset_date != today:
            self.requests_made_today = 0
            self.last_reset_date = today
            self.save()


class SMTPServer(models.Model):
    name = models.CharField(max_length=100)
    host = models.CharField(max_length=255)
    port = models.IntegerField()
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    use_tls = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    daily_limit = models.IntegerField(default=2000)
    messages_sent_today = models.IntegerField(default=0)
    last_reset_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name

    def reset_daily_count(self):
        today = timezone.now().date()
        if self.last_reset_date != today:
            self.messages_sent_today = 0
            self.last_reset_date = today
            self.save()


class WhatsAppAccount(models.Model):
    name = models.CharField(max_length=100)
    phone_number_id = models.CharField(max_length=255)
    access_token = models.CharField(max_length=500)
    is_active = models.BooleanField(default=True)
    daily_limit = models.IntegerField(default=1000)
    messages_sent_today = models.IntegerField(default=0)
    last_reset_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name

    def reset_daily_count(self):
        today = timezone.now().date()
        if self.last_reset_date != today:
            self.messages_sent_today = 0
            self.last_reset_date = today
            self.save()


class MessageQueue(models.Model):
    communication = models.OneToOneField('Communication', on_delete=models.CASCADE)
    priority = models.IntegerField(default=0, db_index=True)
    scheduled_time = models.DateTimeField(db_index=True)
    attempts = models.IntegerField(default=0)
    max_attempts = models.IntegerField(default=3)
    smtp_server = models.ForeignKey(SMTPServer, null=True, blank=True, on_delete=models.SET_NULL)
    whatsapp_account = models.ForeignKey(WhatsAppAccount, null=True, blank=True, on_delete=models.SET_NULL)
    locked_at = models.DateTimeField(null=True, blank=True, db_index=True)
    locked_by = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        app_label = 'communications'
        ordering = ['priority', 'scheduled_time']
        indexes = [
            models.Index(fields=['priority', 'scheduled_time', 'attempts']),
            models.Index(fields=['locked_at', 'attempts']),
        ]
        
    def __str__(self):
        return f"Queue item for {self.communication}"


class Communication(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='communications',
        db_index=True
    )
    business = models.ForeignKey(
        Business,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='communications',
        db_index=True
    )

    EMAIL = "email"
    WHATSAPP = "whatsapp"

    TYPE_CHOICES = [
        (EMAIL, "Email"),
        (WHATSAPP, "WhatsApp"),
    ]

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("queued", "Queued"),
        ("processing", "Processing"),
        ("sent", "Sent"),
        ("failed", "Failed"),
    ]

    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default=EMAIL, db_index=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending", db_index=True)
    recipient = models.CharField(max_length=255, db_index=True)
    content = models.TextField()
    subject = models.CharField(max_length=255, blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)
    whatsapp_message_id = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    smtp_server = models.ForeignKey(SMTPServer, null=True, blank=True, on_delete=models.SET_NULL)
    whatsapp_account = models.ForeignKey(WhatsAppAccount, null=True, blank=True, on_delete=models.SET_NULL)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    sent_at = models.DateTimeField(null=True, blank=True, db_index=True)

    class Meta:
        app_label = 'communications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['type', 'status', 'created_at']),
            models.Index(fields=['user', 'type', 'status']),
            models.Index(fields=['status', 'created_at']),
        ]

    def __str__(self):
        if self.type == self.EMAIL:
            return f"Email to {self.recipient} ({self.status})"
        return f"WhatsApp to {self.recipient} ({self.status})"