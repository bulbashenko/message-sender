from django.urls import path
from .views import EmailView

app_name = "communications"

urlpatterns = [
    # Email endpoints
    path("email/", EmailView.as_view(), name="email-list"),  # GET for history
    path("email/send/", EmailView.as_view(), name="email-send"),  # POST for sending
]
