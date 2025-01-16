from django.urls import path
from .views import EmailView

app_name = "communications"

urlpatterns = [
    path("email/", EmailView.as_view(), name="email-list"),
    path("email/send/", EmailView.as_view(), name="email-send"),
]
