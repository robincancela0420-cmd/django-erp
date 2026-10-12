from django.contrib import admin
from .models import Project

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        "project_code",
        "name",
        "location",
        "status",
        "start_date",
        "target_end_date",
    )

    search_fields = (
        "project_code",
        "name",
        "location",
    )

    list_filter = ("status",)