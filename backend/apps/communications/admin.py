from django.contrib import admin
from .models import Communication


@admin.register(Communication)
class CommunicationAdmin(admin.ModelAdmin):
    list_display = [
        "get_type_icon",
        "status",
        "recipient",
        "get_subject_or_preview",
        "created_at",
        "sent_at",
    ]
    list_filter = ["type", "status", "created_at", "sent_at"]
    search_fields = ["recipient", "subject", "content", "whatsapp_message_id"]
    readonly_fields = [
        "type",
        "created_at",
        "updated_at",
        "sent_at",
        "error_message",
        "whatsapp_message_id",
    ]
    ordering = ["-created_at"]

    def has_add_permission(self, request):
        """Disable manual creation of communications"""
        return False

    def has_change_permission(self, request, obj=None):
        """Disable editing of communications"""
        return False

    def get_type_icon(self, obj):
        """Return an icon based on communication type"""
        icons = {"email": "📧", "whatsapp": "💬"}
        return f"{icons.get(obj.type, '❓')} {obj.type.title()}"

    get_type_icon.short_description = "Type"

    def get_subject_or_preview(self, obj):
        """Return subject for emails or content preview for WhatsApp"""
        if obj.type == "email":
            return obj.subject or "(No subject)"
        return (obj.content[:50] + "...") if len(obj.content) > 50 else obj.content

    get_subject_or_preview.short_description = "Subject/Preview"
