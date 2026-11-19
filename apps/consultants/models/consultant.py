
from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator


def consultant_avatar_path(instance, filename):
    return f"consultants/avatars/{filename}"


class Consultant(models.Model):

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="consultant_profile",
    )

    full_name = models.CharField(max_length=150)

    slug = models.SlugField(
        max_length=180,
        unique=True,
        allow_unicode=True,
    )

    title = models.CharField(max_length=150)

    bio = models.TextField()

    avatar = models.ImageField(
        upload_to=consultant_avatar_path,
        blank=True,
        null=True,
    )

    specialties = models.ManyToManyField(
        "consultants.ConsultantSpecialty",
        related_name="consultants",
        blank=True,
    )

    experience_years = models.PositiveSmallIntegerField(default=0)

    consultation_fee = models.DecimalField(
        max_digits=14, decimal_places=0, default=0, validators=[MinValueValidator(0)],
        help_text="مبلغ به تومان",
    )

    is_active = models.BooleanField(
        default=True,
        db_index=True,
    )

    is_verified = models.BooleanField(default=False)

    display_order = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["display_order", "-created_at"]
        verbose_name = "مشاور"
        verbose_name_plural = "مشاوران"

        constraints = [
            models.CheckConstraint(condition=models.Q(consultation_fee__gte=0), name="consultant_fee_nonnegative"),
        ]

        indexes = [
            models.Index(
                fields=["is_active", "display_order"],
                name="consultant_active_order_idx",
            ),
        ]

    def __str__(self):
        return self.full_name
