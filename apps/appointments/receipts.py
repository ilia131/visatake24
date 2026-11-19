from pathlib import Path
from uuid import uuid4

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.utils.deconstruct import deconstructible
from PIL import Image
from pypdf import PdfReader
from pypdf.errors import PdfReadError
from rest_framework.exceptions import ValidationError


@deconstructible
class ReceiptStorage(FileSystemStorage):
    @property
    def location(self):
        return str(Path(settings.APPOINTMENT_RECEIPT_ROOT).resolve())

    def url(self, name):
        raise ValueError("Receipts are only available through the download API.")


receipt_storage = ReceiptStorage(file_permissions_mode=0o600, directory_permissions_mode=0o700)


def receipt_path(instance, filename):
    return f"{uuid4().hex}{Path(filename).suffix.lower()}"


def validate_receipt(upload):
    if upload.size > 5 * 1024 * 1024:
        raise ValidationError("حجم رسید نباید بیشتر از ۵ مگابایت باشد.")

    extension = Path(upload.name).suffix.lower()
    formats = {".jpg": "JPEG", ".jpeg": "JPEG", ".png": "PNG"}
    try:
        if extension == ".pdf":
            if upload.read(5) != b"%PDF-":
                raise ValueError
            upload.seek(0)
            pdf = PdfReader(upload, strict=True)
            if pdf.is_encrypted or not len(pdf.pages):
                raise ValueError
        elif extension in formats:
            with Image.open(upload, formats=[formats[extension]]) as image:
                image.verify()
        else:
            raise ValueError
    except (ValueError, OSError, SyntaxError, PdfReadError, Image.DecompressionBombError) as exc:
        raise ValidationError("فرمت رسید معتبر نیست.") from exc
    finally:
        upload.seek(0)

    return upload
