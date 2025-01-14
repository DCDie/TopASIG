from django.contrib import admin

from apps.ensurance.models import File


@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ("external_id", "name", "type")
    search_fields = ("external_id", "name")
    list_filter = ("type",)
    readonly_fields = ("external_id", "name", "type")
