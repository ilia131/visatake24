
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.exceptions import NotFound

from apps.visas.models import VisaApplication, VisaApplicationDocument
from apps.visas.api.serializers.document import (
    VisaApplicationDocumentUploadSerializer,
)


class VisaApplicationDocumentListCreateAPIView(generics.ListCreateAPIView):
    queryset = VisaApplicationDocument.objects.none()
    serializer_class = VisaApplicationDocumentUploadSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_application(self):
        tracking_code = self.kwargs.get("tracking_code")

        application = VisaApplication.objects.filter(
            tracking_code=tracking_code,
            user=self.request.user,
        ).first()

        if application is None:
            raise NotFound("درخواست ویزا پیدا نشد.")

        return application

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return VisaApplicationDocument.objects.none()

        application = self.get_application()

        return VisaApplicationDocument.objects.filter(
            application=application
        ).select_related("application")

    def perform_create(self, serializer):
        application = self.get_application()
        serializer.save(application=application)
