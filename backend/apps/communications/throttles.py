from rest_framework.throttling import UserRateThrottle


class EmailRateThrottle(UserRateThrottle):
    rate = '100/day'
    scope = 'email_send'


class WhatsAppRateThrottle(UserRateThrottle):
    rate = '50/day'
    scope = 'whatsapp_send'