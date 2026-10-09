from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        "username",
        "first_name",
        "last_name",
        "email",
        "role",
        "department",
        "is_active",
        "is_staff",
    )

    list_filter = (
        "role",
        "department",
        "is_active",
        "is_staff",
    )

    search_fields = (
        "username",
        "first_name",
        "last_name",
        "email",
        "department",
    )

    fieldsets = UserAdmin.fieldsets + (
        (
            "Construction ERP Information",
            {
                "fields": (
                    "role",
                    "department",
                    "job_title",
                )
            },
        ),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "Construction ERP Information",
            {
                "fields": (
                    "role",
                    "department",
                    "job_title",
                )
            },
        ),
    )