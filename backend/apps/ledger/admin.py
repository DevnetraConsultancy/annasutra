"""Django Admin configuration for Ledger and TraceEvent.

Strictly read-only: events can never be edited or deleted by admins.
"""

from django.contrib import admin
from .models import HashAnchor, TraceEvent


@admin.register(TraceEvent)
class TraceEventAdmin(admin.ModelAdmin):
    list_display = ("event_id", "lot", "lot_seq", "event_type", "event_time", "recorded_at", "org", "sync_status")
    list_filter = ("event_type", "sync_status")
    search_fields = ("event_id", "lot__public_code", "payload")
    readonly_fields = [f.name for f in TraceEvent._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(HashAnchor)
class HashAnchorAdmin(admin.ModelAdmin):
    list_display = ("anchor_id", "anchor_type", "anchor_date", "lot_count", "published_at")
    readonly_fields = [f.name for f in HashAnchor._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
