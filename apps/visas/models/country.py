from django.db import models


class Country(models.Model):

    name = models.CharField(
        max_length=100,
        verbose_name="نام کشور",
    )

    name_en = models.CharField(
        max_length=100,
        verbose_name="نام انگلیسی",
    )

    slug = models.SlugField(
        unique=True,
        max_length=120,
    )

    flag = models.CharField(
        max_length=10,
        blank=True,
        verbose_name="پرچم",
    )

    description = models.TextField(
        blank=True,
        verbose_name="توضیحات",
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "کشور"
        verbose_name_plural = "کشورها"

    def __str__(self):
        return self.name