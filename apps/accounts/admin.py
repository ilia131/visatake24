
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User
from .forms import (
    AdminUserCreationForm,
    AdminUserChangeForm,
)


@admin.register(User)
class CustomUserAdmin(UserAdmin):

    add_form = AdminUserCreationForm
    form = AdminUserChangeForm

    ordering = ("phone_number",)

    list_display = (
        "id",
        "phone_number",
        "role",
        "is_phone_verified",
        "is_active",
        "is_staff",
    )

    list_filter = (
        "role",
        "is_phone_verified",
        "is_active",
        "is_staff",
    )

    search_fields = (
        "phone_number",
        "email",
        "first_name",
        "last_name",
    )

    readonly_fields = (
        "password",
        "last_login",
        "date_joined",
    )

    fieldsets = (
        (
            _("Account"),
            {
                "fields": (
                    "phone_number",
                    "password",
                    "role",
                    "is_phone_verified",
                )
            },
        ),
        (
            _("Personal Information"),
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "email",
                )
            },
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (
            _("Dates"),
            {
                "fields": (
                    "last_login",
                    "date_joined",
                )
            },
        ),
    )

    add_fieldsets = (
        (
            _("Create User"),
            {
                "classes": ("wide",),
                "fields": (
                    "phone_number",
                    "role",
                    "is_active",
                    "is_phone_verified",
                    "password1",
                    "password2",
                ),
            },
        ),
    )
