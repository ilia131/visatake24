
import uuid
import os

from django.db import models
from django.conf import settings
from django.core.files.storage import FileSystemStorage


def get_private_document_storage():
    return FileSystemStorage(location=settings.BASE_DIR / "private_media", base_url=None)


def document_upload_path(instance, filename):
    extension = os.path.splitext(filename)[1].lower()

    return (
        f"visa_documents/"
        f"{instance.application.tracking_code}/"
        f"{uuid.uuid4().hex}{extension}"
    )


class VisaApplicationDocument(models.Model):

    class DocumentType(models.TextChoices):
        PASSPORT = "passport", "پاسپورت"
        PHOTO = "photo", "عکس پرسنلی"
        BANK_STATEMENT = "bank_statement", "گردش حساب"
        EMPLOYMENT = "employment", "گواهی اشتغال"
        TRAVEL_INSURANCE = "travel_insurance", "بیمه مسافرتی"
        OTHER = "other", "سایر مدارک"

    class Status(models.TextChoices):
        PENDING = "pending", "در انتظار بررسی"
        APPROVED = "approved", "تأیید شده"
        REJECTED = "rejected", "رد شده"

    application = models.ForeignKey(
        "visas.VisaApplication",
        on_delete=models.CASCADE,
        related_name="documents",
        verbose_name="درخواست ویزا"
    )

    document_type = models.CharField(
        max_length=30,
        choices=DocumentType.choices,
        verbose_name="نوع مدرک"
    )

    file = models.FileField(
        storage=get_private_document_storage,
        upload_to=document_upload_path,
        verbose_name="فایل مدرک"
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
        verbose_name="وضعیت مدرک"
    )

    admin_notes = models.TextField(
        blank=True,
        verbose_name="یادداشت مدیر"
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-uploaded_at"]
        verbose_name = "مدرک درخواست"
        verbose_name_plural = "مدارک درخواست‌ها"

    def __str__(self):
        return (
            f"{self.application.tracking_code} - "
            f"{self.get_document_type_display()}"
        )
