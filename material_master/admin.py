from django.contrib import admin
from .models import Material

@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "Unit_of_measurement",
        "item_type",
        "created_at",
        "created_by",
    )

    search_fields = ("name",)
    list_filter = ("item_type", "Unit_of_measurement")
    readonly_fields = ("created_at", "created_by")

    def save_model(self, request, obj, form, change):
        if not change and not obj.created_by_id:
            obj.created_by = request.user

        super().save_model(request, obj, form, change)