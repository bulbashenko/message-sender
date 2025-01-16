import requests
from django.conf import settings
import logging

logger = logging.getLogger("apps")


def get_country_from_ip(ip_address):
    """
    Get country code from IP address using ipapi.co
    """
    try:
        response = requests.get(settings.IP_API_URL.format(ip_address))
        if response.status_code == 200:
            data = response.json()
            return data.get("country_code")
        return None
    except Exception as e:
        logger.error(f"Error getting country from IP: {str(e)}")
        return None


def validate_country_restriction(user, ip_address):
    """
    Validate if user is allowed to access from their country
    Returns tuple (is_allowed, country_code)
    """
    country_code = get_country_from_ip(ip_address)
    if not country_code:
        return True, None  # Allow access if country detection fails

    return user.is_country_allowed(country_code), country_code
