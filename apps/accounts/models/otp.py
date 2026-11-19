
import uuid

from django.db import models
from django.utils import timezone


class OTPCode(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    phone_number = models.CharField(
        max_length=16,
        db_index=True,
    )

    code_hash = models.CharField(
        max_length=128,
    )

    expires_at = models.DateTimeField()

    attempts = models.PositiveSmallIntegerField(default=0)

    is_used = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "accounts_otp"
        ordering = ["-created_at"]
        indexes = [
            models.Index(
                fields=["phone_number", "created_at"]
            )
        ]

    @property
    def is_expired(self):
        return timezone.now() >= self.expires_at

    def __str__(self):
        return f"OTP for {self.phone_number}"
