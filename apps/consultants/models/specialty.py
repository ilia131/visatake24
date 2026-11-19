
from django.db import models
from django.utils.text import slugify


class ConsultantSpecialty(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="نام تخصص",
    )

    slug = models.SlugField(
        max_length=120,
        unique=True,
        allow_unicode=True,
    )

    description = models.TextField(
        blank=True,
        verbose_name="توضیحات",
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "تخصص مشاور"
        verbose_name_plural = "تخصص‌های مشاور"

    def __str__(self):
        return self.name
