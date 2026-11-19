from django.http import FileResponse
from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound
from drf_spectacular.utils import extend_schema, OpenApiResponse
from drf_spectacular.types import OpenApiTypes
from apps.visas.models import VisaApplicationDocument


class VisaApplicationDocumentDownloadAPIView(APIView):
    permission_classes = [IsAuthenticated]
    @extend_schema(
        summary="دانلود مدرک درخواست ویزا",
        description="دانلود مدرک توسط مالک درخواست یا مدیر مجاز.",
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.BINARY,
                description="فایل مدرک",
            ),
        },
    )
    def get(self, request, document_id):
        document = get_object_or_404(
            VisaApplicationDocument.objects.select_related(
                "application"
            ),
            id=document_id,
        )

        is_owner = document.application.user_id == request.user.id
        is_admin = request.user.is_staff

        if not is_owner and not is_admin:
            raise NotFound("مدرک موردنظر پیدا نشد.")

        if not document.file:
            raise NotFound("فایل مدرک موجود نیست.")

        return FileResponse(
            document.file.open("rb"),
            as_attachment=True,
            filename=document.file.name.split("/")[-1],
        )