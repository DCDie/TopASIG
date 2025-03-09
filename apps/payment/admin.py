from django.contrib import admin

from .models import QrCode


@admin.register(QrCode)
class QrCodeAdmin(admin.ModelAdmin):
    list_display = ("uuid", "order_id", "type", "amount_type", "status", "created_at")
    search_fields = ("uuid", "order_id", "type", "amount_type", "status")
    list_filter = ("type", "amount_type", "status")
    readonly_fields = ("uuid", "order_id", "created_at", "updated_at")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
