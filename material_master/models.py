from django.conf import settings
from django.db import models

class Material(models.Model):
    class ItemType(models.TextChoices):
        MATERIAL = "material", "Material"
        SERVICE = "service", "Service"

    name = models.CharField(
        max_length=200,
        unique=True
    )

    Unit_of_measurement = models.CharField(
        max_length=50,
    )

    item_type = models.CharField(
        max_length=20,
        choices=ItemType.choices,
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_materials"
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Material Master"
        verbose_name_plural = "Material Master"

    def __str__(self):
        return self.name