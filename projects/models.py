from django.db import models

class Project(models.Model):

    class Status(models.TextChoices):
        PLANNING = "planning", "Planning"
        ACTIVE = "active", "Active"
        ON_HOLD = "on_hold", "On Hold"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    project_code = models.CharField(
        max_length=50,
        unique=True
    )

    name = models.CharField(
        max_length=200,
    )

    location = models.CharField(
        max_length=255,
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PLANNING,
    )

    start_date = models.DateField(
        null=True,
        blank=True
    )

    target_end_date = models.DateField(
        null=True,
        blank=True,
    )

    description = models.TextField(
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["project_code"]
        verbose_name = "Project"
        verbose_name_plural = "Projects"

        def __str__(self):
            return f"{self.project_code} - {self.name}"