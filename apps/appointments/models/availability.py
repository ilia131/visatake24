
from django.db import models
from django.db.models import F, Q

from apps.consultants.models import Consultant


class ConsultantAvailability(models.Model):

    class Status(models.TextChoices):
        AVAILABLE = "available", "آزاد"
        BLOCKED = "blocked", "مسدود"

    consultant = models.ForeignKey(
        Consultant,
        on_delete=models.PROTECT,
        related_name="availabilities",
    )

    start_at = models.DateTimeField()
    end_at = models.DateTimeField()

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.AVAILABLE,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["start_at"]

        constraints = [
            models.CheckConstraint(
                condition=Q(end_at__gt=F("start_at")),
                name="availability_end_after_start",
            ),
            models.UniqueConstraint(
                fields=["consultant", "start_at", "end_at"],
                name="unique_consultant_availability",
            ),
        ]

        indexes = [
            models.Index(
                fields=["consultant", "status", "start_at"],
                name="availability_lookup_idx",
            ),
        ]

    def __str__(self):
        return f"{self.consultant} - {self.start_at}"
