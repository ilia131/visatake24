import uuid

from django.conf import settings
from django.db import models


def generate_tracking_code():
    return f"VY-{uuid.uuid4().hex[:16].upper()}"


class VisaApplication(models.Model):

    class Status(models.TextChoices):
        SUBMITTED = "submitted", "ثبت شده"
        UNDER_REVIEW = "under_review", "در حال بررسی"
        NEED_INFO = "need_info", "نیازمند اطلاعات بیشتر"
        APPROVED = "approved", "تأیید شده"
        REJECTED = "rejected", "رد شده"
        COMPLETED = "completed", "تکمیل شده"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="visa_applications",
        verbose_name="متقاضی",
    )

    country = models.ForeignKey(
        "visas.Country",
        on_delete=models.PROTECT,
        related_name="applications",
        verbose_name="کشور مقصد",
    )

    tracking_code = models.CharField(
        max_length=30,
        unique=True,
        default=generate_tracking_code,
        editable=False,
        db_index=True,
        verbose_name="کد پیگیری",
    )

    visa_type = models.CharField(
        max_length=100,
        verbose_name="نوع ویزا",
    )

    travel_date = models.DateField(
        verbose_name="تاریخ سفر",
    )

    return_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="تاریخ بازگشت",
    )

    purpose = models.TextField(
        verbose_name="هدف سفر",
    )

    additional_notes = models.TextField(
        blank=True,
        verbose_name="توضیحات تکمیلی",
    )

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.SUBMITTED,
        db_index=True,
        verbose_name="وضعیت درخواست",
    )

    admin_notes = models.TextField(
        blank=True,
        verbose_name="یادداشت مدیر",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
    )

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "درخواست ویزا"
        verbose_name_plural = "درخواست‌های ویزا"

    def __str__(self):
        return f"{self.tracking_code} - {self.user}"