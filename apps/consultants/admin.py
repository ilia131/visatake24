
from django.contrib import admin
from .models import Consultant


@admin.register(Consultant)
class ConsultantAdmin(admin.ModelAdmin):
    list_display = (
        "full_name",
        "title",
        "experience_years",
        "is_active",
        "created_at",
    )

    list_filter = ("is_active",)
    search_fields = ("full_name", "title", "specialties")
    ordering = ("-created_at",)
