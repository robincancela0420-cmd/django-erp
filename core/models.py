from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):

    class Role(models.TextChoices):
        SYSTEM_ADMIN = "system_admin", "System Admin"
        PROJECT_ENGINEER = "project_engineer", "Project Engineer"
        PROJECT_MANAGER  = "project_manager", "Project Manager"
        WAREHOUSEMAN = "warehouseman", "Warehouseman"
        WAREHOUSE_MANAGER = "warehouse_manager", "Warehouse Manager"
        PROCUREMENT = "procurement", "Procurement"
        QS_ENGINEER = "qs_engineer", "QS Engineer"
        ACCOUNTANT = "accountant", "Accountant"
        EXECUTIVE = "executive", "Executive"
        OTHER = "other", "Other"

    role = models.CharField(
        max_length=30,
        choices=Role.choices,
        blank=True
    )

    department = models.CharField(
        max_length=100,
        blank=True,
    )

    job_title = models.CharField(
        max_length=100,
        blank=True
    )

    def __str__(self):
        return self.get_full_name() or self.username

class UserPagePermission(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="page_permissions",
    )

    page_key = models.CharField(max_length=100)

    can_view = models.BooleanField(default=False)
    can_add = models.BooleanField(default=False)
    can_edit = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "page_key"],
                name="unique_user_page_permission",
            )
        ]

    def __str__(self):
        return f"{self.user.username} - {self.page_key}"