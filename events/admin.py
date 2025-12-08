from django.contrib import admin

from .models import Event


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "creator", "category", "status", "scheduled_date")
    list_filter = ("status", "category", "created_at")
    search_fields = ("title", "description", "creator__username")
    date_hierarchy = "scheduled_date"
