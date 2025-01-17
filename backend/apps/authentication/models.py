from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(unique=True, blank=False, null=False)
    facebook_id = models.CharField(max_length=150, blank=True, null=True, unique=True)
    allowed_countries = models.CharField(max_length=255, blank=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        db_table = "custom_user"

    def save(self, *args, **kwargs):
        if self.email:
            self.email = self.email.lower()
        super().save(*args, **kwargs)

    def is_country_allowed(self, country_code):
        if not self.allowed_countries:
            return True
        return country_code in self.allowed_countries.split(",")
