
from django.conf import settings
from django.db import models
from django.db.models import Q


class ConsultantAssignment(models.Model):

    class Status(models.TextChoices):
        ASSIGNED = "assigned", "ارجاع شده"
        IN_PROGRESS = "in_progress", "در حال بررسی"
        NEEDS_DOCUMENTS = "needs_documents", "نیازمند مدارک"
        COMPLETED = "completed", "تکمیل شده"
        REJECTED = "rejected", "رد شده"

    application = models.ForeignKey(
        "visas.VisaApplication",
        on_delete=models.PROTECT,
        related_name="consultant_assignments",
    )

    consultant = models.ForeignKey(
        "consultants.Consultant",
        on_delete=models.PROTECT,
        related_name="assignments",
    )

    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_consultant_assignments",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ASSIGNED,
        db_index=True,
    )

    is_active = models.BooleanField(default=True, db_index=True)

    admin_note = models.TextField(blank=True)
    consultant_note = models.TextField(blank=True)

    assigned_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-assigned_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["application"],
                condition=Q(is_active=True),
                name="unique_active_consultant_assignment",
            ),
        ]
        indexes = [
            models.Index(
                fields=["consultant", "is_active", "status"],
                name="consultant_assignment_idx",
            ),
        ]

    def __str__(self):
        return f"{self.application_id} - {self.consultant.full_name}"
