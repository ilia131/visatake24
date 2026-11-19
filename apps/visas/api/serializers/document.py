
from rest_framework import serializers

from apps.visas.models import VisaApplicationDocument


class VisaApplicationDocumentUploadSerializer(
    serializers.ModelSerializer
):
    class Meta:
        model = VisaApplicationDocument
        fields = [
            "id",
            "document_type",
            "file",
            "status",
            "uploaded_at",
        ]
        read_only_fields = [
            "id",
            "status",
            "uploaded_at",
        ]

    def validate_file(self, file):
        max_size = 5 * 1024 * 1024

        allowed_extensions = [
            ".pdf",
            ".jpg",
            ".jpeg",
            ".png",
        ]

        import os

        extension = os.path.splitext(file.name)[1].lower()

        if extension not in allowed_extensions:
            raise serializers.ValidationError(
                "فرمت فایل مجاز نیست."
            )

        if file.size > max_size:
            raise serializers.ValidationError(
                "حجم فایل نباید بیشتر از ۵ مگابایت باشد."
            )

        return file
