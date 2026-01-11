# Admin del sistema de xat
from django.contrib import admin

from .models import ChatMessage


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    """Admin pel model ChatMessage."""

    list_display = [
        "id",
        "user",
        "event",
        "message_preview",
        "created_at",
        "is_deleted",
        "is_highlighted",
    ]
    list_filter = ["is_deleted", "is_highlighted", "created_at", "event"]
    search_fields = ["message", "user__username", "event__title"]
    readonly_fields = ["created_at"]
    ordering = ["-created_at"]

    def message_preview(self, obj):
        """Retorna les primeres 50 lletres del missatge."""
        return obj.message[:50] + "..." if len(obj.message) > 50 else obj.message

    message_preview.short_description = "Missatge"
