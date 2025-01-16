from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse


def health_check(request):
    return HttpResponse("OK", content_type="text/plain")


def index(request):
    return HttpResponse("Welcome to Django API", content_type="text/plain")


urlpatterns = [
    path("", index),  # Root URL pattern
    path("health/", health_check),
    path("admin/", admin.site.urls),
    path("api/auth/", include("apps.authentication.urls")),
    path("api/communications/", include("apps.communications.urls")),
]
