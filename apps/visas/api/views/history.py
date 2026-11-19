
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound, PermissionDenied

from apps.visas.models import (
    VisaApplication,
    VisaApplicationStatusHistory,
)
from apps.visas.api.serializers.history import (
    VisaApplicationHistorySerializer,
)


class VisaApplicationHistoryAPIView(generics.ListAPIView):
    serializer_class = VisaApplicationHistorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        tracking_code = self.kwargs["tracking_code"]

        application = (
            VisaApplication.objects
            .filter(tracking_code=tracking_code)
            .first()
        )

        if application is None:
            raise NotFound("پرونده پیدا نشد.")

        user = self.request.user

        if not (user.is_staff or application.user_id == user.id):
            raise PermissionDenied(
                "شما اجازه مشاهده تاریخچه این پرونده را ندارید."
            )

        return (
            VisaApplicationStatusHistory.objects
            .filter(application=application)
            .select_related("changed_by")
            .order_by("-created_at")
        )
