from django.db import models
from django.conf import settings
from django.utils import timezone

class MaterialRequisition(models.Model):

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        FOR_APPROVAL = "for_approval", "For Approval"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        PARTIALLY_ORDERED = "partially_ordered", "Partially Ordered"
        FULLY_ORDERED = "fully_ordered", "Full Ordered"

    requisition_number = models.CharField(
        max_length=30,
        unique=True,
        null=True,
        blank=True,
    )

    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.PROTECT,
        related_name="material_requisitions",
    )

    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="submitted_material_requisitions",
    )

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.DRAFT
    )

    qs_verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="qs_verified_requisitions",
        null=True,
        blank=True,
    )

    qs_verified_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name = "approved_material_requisitions",
        null=True,
        blank=True,
    )

    approved_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    remarks = models.TextField(blank=True)

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["created_at"]
        verbose_name = "Material Requisition"
        verbose_name_plural = "Material Requisitions"

    def __str__(self):
        return self.requisition_number or f"MR Draft #{self.pk}"

    def save(self, *args, **kwargs):
            if not self.requisition_number:
                if self.pk is None:
                    super().save(*args, **kwargs)
    
                self.requisition_number = (
                    f"MR-{timezone.localdate().year}-{self.pk:04d}"
                )
    
                super().save(update_fields=["requisition_number"])
                return
    
            super().save(*args, **kwargs)

    def submit_for_approval(self, user):
        if user.role != "qs_engineer":
            raise PermissionError(
                "Only QS Engineer can submit requisition"
            )

        if self.status != self.Status.DRAFT:
            raise ValueError(
                "Only draft requisition can be subumitted."
            )

        if not self.items.exists():
            raise ValueError(
                "Add at least one material before submitting"
            )

        self.status = self.status.FOR_APPROVAL
        self.qs_verified_by = user
        self.qs_verified_at = timezone.now()

        self.save(update_fields=[
            "status",
            "qs_verified_by",
            "qs_verified_at",
            "updated_at",
        ])

    def approve(self, user):
        if user.role != "project_manager":
            raise PermissionError(
                "Only Project Manager can approved requisitions."
            )

        if self.statis != self.Status.FOR_APPROVAL:
            raise ValueError(
                "Only submitted requisitions can be approved."
            )

        self.status = self.Status.APPROVED
        self.approved_by = user
        self.approved_at = timezone.now()

        self.save(update_fields = [
            "status",
            "approved_by",
            "approved_at",
            "updated_at",
        ])

    def reject(self, user, remarks=""):
        if user.role != "project_manager":
            raise PermissionError(
                "Only Project Manager can reject requisition."
            )

        if self.status != self.Status.FOR_APPROVAL:
            raise ValueError(
                "Only Submitted requisition can be rejected."
            )

        self.status = self.Status.REJECTED
        self.approved_by = user
        self.approved_at = timezone.now()
        self.remarks = remarks

        self.save(update_fields = [
            "status",
            "approved_by",
            "approved_at",
            "remarls",
            "updated_at",
        ])

class MaterialRequisitionItem(models.Model):
    requisition = models.ForeignKey(
        MaterialRequisition,
        on_delete=models.CASCADE,
        related_name="items",
    )

    material = models.ForeignKey(
        "material_master.Material",
        on_delete=models.PROTECT,
        related_name="requisition_items",
    )

    quantity = models.DecimalField(
        max_digits=14,
        decimal_places=2,
    )

    estimated_unit_price = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0
    )

    remarks = models.CharField(
        max_length=255,
        blank=True,
    )

    class Meta:
        ordering = ["id"]
        verbose_name = "Requisition Item"
        verbose_name_plural = "Requisition Items"

    def __str__(self):
        return (
            f"{self.material.name}"
            f"{self.quantity}"
            f"{self.material.Unit_of_measurement}"
        )

    def save(self, *args, **kwargs):
        if self.requisition_id:
            if self.requisition.status != MaterialRequisition.Status.DRAFT:
                raise ValueError(
                    "Submitted requisition items cannot be deleted."
                )
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.requisition.status != MaterialRequisition.Status.DRAFT:
            raise ValueError(
                "Submitted requisition utems cannot be deleted."
            )

        super().delete(*args, **kwargs)