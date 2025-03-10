from django.contrib import admin

from apps.ensurance.models import File, MedicalInsuranceCompany, RCACompany


@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ("external_id", "name", "type")
    search_fields = ("external_id", "name")
    list_filter = ("type",)
    readonly_fields = ("external_id", "name", "type")


@admin.register(RCACompany)
class RCACompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "idno", "is_active", "is_public", "logo")
    search_fields = ("name", "idno")
    list_filter = ("is_active", "is_public")
    readonly_fields = ("name", "idno")
    fields = ("name", "idno", "is_active", "is_public", "logo")


@admin.register(MedicalInsuranceCompany)
class MedicalInsuranceCompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "idno", "is_active", "is_public", "logo")
    search_fields = ("name", "idno")
    list_filter = ("is_active", "is_public")
    fields = ("name", "idno", "is_active", "is_public", "logo")
