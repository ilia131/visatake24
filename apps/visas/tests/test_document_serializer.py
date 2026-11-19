
import pytest

from django.core.files.uploadedfile import SimpleUploadedFile

from apps.visas.api.serializers.document import (
    VisaApplicationDocumentUploadSerializer,
)


@pytest.mark.django_db
def test_valid_pdf_document():
    file = SimpleUploadedFile(
        "passport.pdf",
        b"sample pdf content",
        content_type="application/pdf",
    )

    serializer = VisaApplicationDocumentUploadSerializer(
        data={
            "document_type": "passport",
            "file": file,
        }
    )

    assert serializer.is_valid()


@pytest.mark.django_db
def test_invalid_document_extension():
    file = SimpleUploadedFile(
        "passport.exe",
        b"sample content",
        content_type="application/octet-stream",
    )

    serializer = VisaApplicationDocumentUploadSerializer(
        data={
            "document_type": "passport",
            "file": file,
        }
    )

    assert not serializer.is_valid()
    assert "file" in serializer.errors


@pytest.mark.django_db
def test_document_size_limit():
    file = SimpleUploadedFile(
        "large.pdf",
        b"x" * (6 * 1024 * 1024),
        content_type="application/pdf",
    )

    serializer = VisaApplicationDocumentUploadSerializer(
        data={
            "document_type": "passport",
            "file": file,
        }
    )

    assert not serializer.is_valid()
    assert "file" in serializer.errors
