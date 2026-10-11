"""Django Admin configuration for security and operational Alerts."""

from django.contrib import admin
from .models import Alert, ScanLog


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ("alert_id", "rule", "severity", "status", "lot", "created_at")
    list_filter = ("severity", "status", "rule")
    search_fields = ("rule", "lot__public_code")
    readonly_fields = ("alert_id", "rule", "lot", "severity", "detail", "created_at")
    actions = ["mark_reviewing", "mark_closed"]

    @admin.action(description="Mark selected alerts as REVIEWING")
    def mark_reviewing(self, request, queryset):
        queryset.update(status="REVIEWING")

    @admin.action(description="Close selected alerts")
    def mark_closed(self, request, queryset):
        queryset.update(status="CLOSED")


@admin.register(ScanLog)
class ScanLogAdmin(admin.ModelAdmin):
    list_display = ("scan_id", "serial", "user_id", "scanned_at", "result")
    list_filter = ("result",)
    search_fields = ("serial",)
    readonly_fields = ("scan_id", "serial", "user_id", "scanned_at", "coarse_area", "result")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
