from django.urls import path
from .views import EmailView, WhatsAppView, MessageHistoryView

app_name = "communications"

urlpatterns = [
    # Message history endpoint
    path("history/", MessageHistoryView.as_view(), name="message-history"),
    
    # Messaging endpoints
    path("email/", EmailView.as_view(), name="email-send"),
    path("whatsapp/", WhatsAppView.as_view(), name="whatsapp-send"),
]
