
from django.contrib import admin

from apps.visas.models import Country, VisaApplication


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "name_en",
        "slug",
        "is_active",
    )

    list_filter = ("is_active",)

    search_fields = (
        "name",
        "name_en",
    )

    prepopulated_fields = {
        "slug": ("name_en",),
    }


@admin.register(VisaApplication)
class VisaApplicationAdmin(admin.ModelAdmin):

    list_display = (
        "tracking_code",
        "user",
        "country",
        "visa_type",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
        "country",
        "created_at",
    )

    search_fields = (
        "tracking_code",
        "user__phone_number",
        "country__name",
    )

    readonly_fields = (
        "tracking_code",
        "created_at",
        "updated_at",
    )

    list_per_page = 25