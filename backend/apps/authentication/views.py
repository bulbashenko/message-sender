import requests
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model, authenticate
from django.conf import settings
from django.db import IntegrityError
import logging

logger = logging.getLogger("apps.authentication")
User = get_user_model()


def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0]
    return request.META.get("REMOTE_ADDR")


class RegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email", "").lower()
        password = request.data.get("password")

        if not email or not password:
            return Response(
                {"success": False, "error": "Please provide both email and password"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            username = email.split("@")[0]
            user = User.objects.create_user(
                username=username, email=email, password=password
            )
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "success": True,
                    "data": {
                        "refresh": str(refresh),
                        "access": str(refresh.access_token),
                    },
                },
                status=status.HTTP_201_CREATED,
            )
        except IntegrityError:
            return Response(
                {"success": False, "error": "Email already registered"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email", "").lower()
        password = request.data.get("password")

        if not email or not password:
            return Response(
                {"success": False, "error": "Please provide both email and password"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = authenticate(request, username=email, password=password)
        if not user:
            return Response(
                {"success": False, "error": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        client_ip = get_client_ip(request)
        user.last_login_ip = client_ip
        user.save()

        try:
            response = requests.get(settings.IP_API_URL.format(client_ip))
            if response.status_code == 200:
                country_code = response.json().get("country_code")
                if country_code and not user.is_country_allowed(country_code):
                    return Response(
                        {
                            "success": False,
                            "error": f"Access not allowed from {country_code}",
                        },
                        status=status.HTTP_403_FORBIDDEN,
                    )
        except Exception as e:
            logger.error(f"IP lookup error: {str(e)}")

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "success": True,
                "data": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
            }
        )


class FacebookLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        fb_access_token = request.data.get("access_token")
        if not fb_access_token:
            return Response(
                {"success": False, "error": "Facebook access token is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            fb_response = requests.get(
                f"https://graph.facebook.com/me",
                params={
                    "fields": "id,email",
                    "access_token": fb_access_token,
                },
            )
            fb_data = fb_response.json()

            if "error" in fb_data:
                return Response(
                    {"success": False, "error": "Invalid Facebook token"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:
                user = User.objects.get(facebook_id=fb_data["id"])
            except User.DoesNotExist:
                email = fb_data.get("email", "").lower()
                username = email.split("@")[0] if email else f"fb_{fb_data['id']}"

                user = User.objects.create_user(
                    username=username,
                    email=email,
                    facebook_id=fb_data["id"],
                )

            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "success": True,
                    "data": {
                        "refresh": str(refresh),
                        "access": str(refresh.access_token),
                    },
                }
            )

        except Exception as e:
            logger.error(f"Facebook login error: {str(e)}")
            return Response(
                {"success": False, "error": "Failed to authenticate with Facebook"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class LogoutView(APIView):
    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response(
                    {"success": False, "error": "Refresh token is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {"success": True, "data": {"message": "Successfully logged out"}},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"success": False, "error": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )
