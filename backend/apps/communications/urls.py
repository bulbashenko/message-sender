from django.urls import path
from .views import EmailView, WhatsAppView

app_name = "communications"

urlpatterns = [
    path("email/", EmailView.as_view(), name="email-list"),
    path("email/send/", EmailView.as_view(), name="email-send"),
    path("whatsapp/", WhatsAppView.as_view(), name="whatsapp-list"),
    path("whatsapp/send/", WhatsAppView.as_view(), name="whatsapp-send"),
]
