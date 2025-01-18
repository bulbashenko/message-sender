from rest_framework.throttling import UserRateThrottle


class EmailRateThrottle(UserRateThrottle):
    """
    Throttle for email sending endpoints.
    Limits users to 100 email requests per day.
    """
    rate = '100/day'
    scope = 'email_send'


class WhatsAppRateThrottle(UserRateThrottle):
    """
    Throttle for WhatsApp sending endpoints.
    Limits users to 50 WhatsApp requests per day.
    """
    rate = '50/day'
    scope = 'whatsapp_send'