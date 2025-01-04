from django.contrib import admin

from .models import QrCode


@admin.register(QrCode)
class QrCodeAdmin(admin.ModelAdmin):
    list_display = ("uuid", "qr_type", "amount_type", "status", "created_at")
    search_fields = ("uuid", "qr_type", "amount_type", "status")
    list_filter = ("qr_type", "amount_type", "status")
    readonly_fields = ("uuid", "created_at", "updated_at")
