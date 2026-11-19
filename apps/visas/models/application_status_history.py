
from django.conf import settings
from django.db import models
from apps.visas.models.visa_application import VisaApplication

class VisaApplicationStatusHistory(models.Model):
    application = models.ForeignKey(
        "visas.VisaApplication",
        on_delete=models.CASCADE,
        related_name="status_history",
        verbose_name="درخواست ویزا"
    )

    previous_status = models.CharField(
        max_length=30,
        choices=VisaApplication.Status.choices,
        blank=True,
        verbose_name="وضعیت قبلی"
    )

    new_status = models.CharField(
        max_length=30,
        choices=VisaApplication.Status.choices,
        verbose_name="وضعیت جدید"
    )

    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="visa_status_changes",
        verbose_name="تغییردهنده"
    )

    note = models.TextField(
        blank=True,
        verbose_name="توضیحات تغییر"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name="زمان تغییر"
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "تاریخچه وضعیت درخواست"
        verbose_name_plural = "تاریخچه وضعیت درخواست‌ها"

    def __str__(self):
        return (
            f"{self.application.tracking_code}: "
            f"{self.previous_status} → {self.new_status}"
        )
