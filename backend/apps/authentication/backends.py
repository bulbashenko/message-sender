from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from .utils import validate_country_restriction
import logging

logger = logging.getLogger("apps")
User = get_user_model()


class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Check if the username parameter contains an email
            user = User.objects.get(Q(email=username) | Q(username=username))
            if user.check_password(password):
                # Get client IP
                ip_address = self.get_client_ip(request)
                if ip_address:
                    # Validate country restriction
                    is_allowed, country_code = validate_country_restriction(
                        user, ip_address
                    )
                    if not is_allowed:
                        logger.warning(
                            f"Access denied from country {country_code} for user {user.email}"
                        )
                        return None

                    # Update last login IP
                    user.last_login_ip = ip_address
                    user.save(update_fields=["last_login_ip"])

                return user
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    def get_client_ip(self, request):
        """
        Get client IP from request
        """
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip
