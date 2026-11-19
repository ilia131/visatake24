from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound

from apps.dashboard.selectors.applications import (
    get_user_applications,
    get_user_application_detail,
)
from apps.dashboard.api.serializers.application import (
    ApplicationListSerializer,
    ApplicationDetailSerializer,
    ApplicationHistorySerializer,
)


class DashboardApplicationListAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ApplicationListSerializer

    def get_queryset(self):
        return get_user_applications(self.request.user)


class DashboardApplicationDetailAPIView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ApplicationDetailSerializer
    lookup_field = "tracking_code"

    def get_object(self):
        application = get_user_application_detail(
            self.request.user,
            self.kwargs["tracking_code"],
        )

        if application is None:
            raise NotFound("پرونده پیدا نشد.")

        return application


class DashboardApplicationHistoryAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ApplicationHistorySerializer

    def get_queryset(self):
        application = get_user_application_detail(
            self.request.user,
            self.kwargs["tracking_code"],
        )

        if application is None:
            raise NotFound("پرونده پیدا نشد.")

        return application.status_history.all()