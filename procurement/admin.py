from django.contrib import admin, messages
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.http import HttpResponseRedirect
from django.urls import path, reverse

from .models import MaterialRequisition, MaterialRequisitionItem


def is_system_admin(user):
    return user.is_superuser or getattr(user, "role", "") == "system_admin"


def user_role(user):
    return getattr(user, "role", "")


class MaterialRequisitionItemInline(admin.TabularInline):
    model = MaterialRequisitionItem
    extra = 1
    autocomplete_fields = ["material"]
    fields = ("material", "quantity", "estimated_unit_price", "remarks")

    def get_extra(self, request, obj=None, **kwargs):
        if obj and obj.status != MaterialRequisition.Status.DRAFT:
            return 0
        return 1

    def has_add_permission(self, request, obj=None):
        if not (is_system_admin(request.user) or user_role(request.user) == "qs_engineer"):
            return False
        if obj and obj.status != MaterialRequisition.Status.DRAFT:
            return False
        return super().has_add_permission(request, obj)

    def has_change_permission(self, request, obj=None):
        if not (is_system_admin(request.user) or user_role(request.user) == "qs_engineer"):
            return False
        if obj and obj.status != MaterialRequisition.Status.DRAFT:
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if not (is_system_admin(request.user) or user_role(request.user) == "qs_engineer"):
            return False
        if obj and obj.status != MaterialRequisition.Status.DRAFT:
            return False
        return super().has_delete_permission(request, obj)


@admin.register(MaterialRequisition)
class MaterialRequisitionAdmin(admin.ModelAdmin):
    change_form_template = "admin/procurement/materialrequisition/change_form.html"

    list_display = (
        "requisition_number",
        "project",
        "requested_by",
        "status",
        "created_at",
    )
    search_fields = ("requisition_number", "project__name")
    list_filter = ("status", "created_at")
    inlines = [MaterialRequisitionItemInline]

    readonly_fields = (
        "requisition_number",
        "requested_by",
        "status",
        "qs_verified_by",
        "qs_verified_at",
        "approved_by",
        "approved_at",
        "created_at",
        "updated_at",
    )

    def get_fieldsets(self, request, obj=None):
        if obj is None:
            return (
                (
                    "Requisition Details",
                    {
                        "fields": ("project",),
                    },
                ),
                (
                    "Remarks",
                    {
                        "fields": ("remarks",),
                    },
                ),
            )

        return (
            (
                "Requisition Details",
                {
                    "fields": (
                        "requisition_number",
                        "project",
                        "requested_by",
                        "status",
                    ),
                },
            ),
            (
                "Approval History",
                {
                    "classes": ("collapse",),
                    "fields": (
                        "qs_verified_by",
                        "qs_verified_at",
                        "approved_by",
                        "approved_at",
                        "created_at",
                        "updated_at",
                    ),
                },
            ),
            (
                "Remarks",
                {
                    "fields": ("remarks",),
                },
            ),
        )

    def has_view_permission(self, request, obj=None):
        if is_system_admin(request.user):
            return True
        if user_role(request.user) in {
            "project_engineer", "qs_engineer", "project_manager", "procurement"
        }:
            return super().has_view_permission(request, obj)
        return False

    def has_add_permission(self, request):
        if is_system_admin(request.user):
            return True
        if user_role(request.user) != "qs_engineer":
            return False
        return super().has_add_permission(request)

    def has_change_permission(self, request, obj=None):
        if is_system_admin(request.user):
            return obj is None or obj.status == MaterialRequisition.Status.DRAFT
        if user_role(request.user) == "qs_engineer":
            if obj and obj.status != MaterialRequisition.Status.DRAFT:
                return False
            return super().has_change_permission(request, obj)
        return False

    def has_delete_permission(self, request, obj=None):
        if is_system_admin(request.user):
            return obj is None or obj.status == MaterialRequisition.Status.DRAFT
        if user_role(request.user) != "qs_engineer":
            return False
        if obj and obj.status != MaterialRequisition.Status.DRAFT:
            return False
        return super().has_delete_permission(request, obj)

    def save_model(self, request, obj, form, change):
        if not change:
            if not (is_system_admin(request.user) or user_role(request.user) == "qs_engineer"):
                raise PermissionDenied
            obj.requested_by = request.user
            obj.status = MaterialRequisition.Status.DRAFT
        else:
            old_obj = MaterialRequisition.objects.get(pk=obj.pk)
            if old_obj.status != MaterialRequisition.Status.DRAFT:
                raise ValidationError("Submitted requisitions cannot be edited.")
            if obj.status != old_obj.status:
                raise ValidationError("Status changes must use workflow actions.")
            obj.requested_by = old_obj.requested_by
        super().save_model(request, obj, form, change)

    def get_urls(self):
        custom_urls = [
            path(
                "<int:object_id>/submit/",
                self.admin_site.admin_view(self.submit_view),
                name="procurement_materialrequisition_submit",
            ),
            path(
                "<int:object_id>/approve/",
                self.admin_site.admin_view(self.approve_view),
                name="procurement_materialrequisition_approve",
            ),
            path(
                "<int:object_id>/reject/",
                self.admin_site.admin_view(self.reject_view),
                name="procurement_materialrequisition_reject",
            ),
        ]
        return custom_urls + super().get_urls()

    def _get_requisition(self, request, object_id):
        obj = self.get_object(request, object_id)
        if obj is None:
            raise ValidationError("Requisition not found.")
        return obj

    def _return_to_change(self, object_id):
        url = reverse(
            "admin:procurement_materialrequisition_change",
            args=[object_id],
        )
        return HttpResponseRedirect(url)

    def submit_view(self, request, object_id):
        if request.method != "POST":
            raise PermissionDenied
        obj = self._get_requisition(request, object_id)
        try:
            with transaction.atomic():
                obj.submit_for_approval(request.user)
            self.message_user(
                request, "FOR APPROVAL OF PROJECT MANAGER", messages.SUCCESS
            )
        except (PermissionError, ValueError, ValidationError) as exc:
            self.message_user(request, str(exc), messages.ERROR)
        return self._return_to_change(object_id)

    def approve_view(self, request, object_id):
        if request.method != "POST":
            raise PermissionDenied
        obj = self._get_requisition(request, object_id)
        try:
            with transaction.atomic():
                obj.approve(request.user)
            self.message_user(
                request, "PM APPROVED Purchase Request", messages.SUCCESS
            )
        except (PermissionError, ValueError, ValidationError) as exc:
            self.message_user(request, str(exc), messages.ERROR)
        return self._return_to_change(object_id)

    def reject_view(self, request, object_id):
        if request.method != "POST":
            raise PermissionDenied
        obj = self._get_requisition(request, object_id)
        try:
            with transaction.atomic():
                obj.reject(request.user, obj.remarks)
            self.message_user(
                request, "Purchase Request rejected.", messages.WARNING
            )
        except (PermissionError, ValueError, ValidationError) as exc:
            self.message_user(request, str(exc), messages.ERROR)
        return self._return_to_change(object_id)


@admin.register(MaterialRequisitionItem)
class MaterialRequisitionItemAdmin(admin.ModelAdmin):
    list_display = (
        "get_requisition_number",
        "material",
        "quantity",
        "estimated_unit_price",
    )
    search_fields = ("requisition__requisition_number", "material__name")
    autocomplete_fields = ["material"]

    @admin.display(description="Requisition Number")
    def get_requisition_number(self, obj):
        return obj.requisition.requisition_number

    def has_view_permission(self, request, obj=None):
        if is_system_admin(request.user):
            return True
        if user_role(request.user) in {
            "project_engineer", "qs_engineer", "project_manager", "procurement"
        }:
            return super().has_view_permission(request, obj)
        return False

    def has_add_permission(self, request):
        if is_system_admin(request.user):
            return True
        if user_role(request.user) != "qs_engineer":
            return False
        return super().has_add_permission(request)

    def has_change_permission(self, request, obj=None):
        if is_system_admin(request.user):
            return obj is None or obj.requisition.status == MaterialRequisition.Status.DRAFT
        if user_role(request.user) != "qs_engineer":
            return False
        if obj and obj.requisition.status != MaterialRequisition.Status.DRAFT:
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if is_system_admin(request.user):
            return obj is None or obj.requisition.status == MaterialRequisition.Status.DRAFT
        if user_role(request.user) != "qs_engineer":
            return False
        if obj and obj.requisition.status != MaterialRequisition.Status.DRAFT:
            return False
        return super().has_delete_permission(request, obj)