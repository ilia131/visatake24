
from django.conf import settings
from django.db import models


class VisaApplicationHistory(models.Model):

    application = models.ForeignKey(
        "visas.VisaApplication",
        on_delete=models.CASCADE,
        related_name="history",
    )

    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="visa_history_changes",
    )

    old_status = models.CharField(max_length=50, blank=True)
    new_status = models.CharField(max_length=50)

    description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(
                fields=["application", "-created_at"],
                name="visa_history_app_date_idx",
            ),
        ]

    def __str__(self):
        return f"{self.application_id}: {self.old_status} -> {self.new_status}"
