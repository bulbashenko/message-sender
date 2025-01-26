from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from .views import (
    EmailView,
    WhatsAppView,
    MessageHistoryView,
    BusinessViewSet,
    SocialMediaProfileViewSet,
    SMTPServerViewSet,
    WhatsAppAccountViewSet,
    MessageQueueView,
    BulkMessageView,
    SocialAPIConfigViewSet
)

app_name = "communications"

router = DefaultRouter()
router.register(r'businesses', BusinessViewSet, basename='business')
router.register(r'smtp-servers', SMTPServerViewSet, basename='smtp-server')
router.register(r'whatsapp-accounts', WhatsAppAccountViewSet, basename='whatsapp-account')
router.register(r'social-configs', SocialAPIConfigViewSet, basename='social-config')

business_router = routers.NestedDefaultRouter(router, r'businesses', lookup='business')
business_router.register(r'social-profiles', SocialMediaProfileViewSet, basename='business-social-profile')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(business_router.urls)),
    
    path("email/", EmailView.as_view(), name="email-send"),
    path("whatsapp/", WhatsAppView.as_view(), name="whatsapp-send"),
    path("bulk/", BulkMessageView.as_view(), name="bulk-send"),
    
    path("history/", MessageHistoryView.as_view(), name="message-history"),
    path("queue/", MessageQueueView.as_view(), name="message-queue"),
    
]