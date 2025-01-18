from django.urls import path
from .views import EmailView, WhatsAppView, MessageHistoryView

app_name = "communications"

urlpatterns = [
    path("history/", MessageHistoryView.as_view(), name="message-history"),
    
    path("email/", EmailView.as_view(), name="email-send"),
    path("whatsapp/", WhatsAppView.as_view(), name="whatsapp-send"),
]
