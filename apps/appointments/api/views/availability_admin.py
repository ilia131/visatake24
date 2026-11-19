
from rest_framework import generics
from rest_framework.permissions import IsAdminUser

from apps.appointments.models import ConsultantAvailability
from apps.appointments.api.serializers.availability import (
    AvailabilityCreateSerializer,
    AvailabilitySerializer,
)


class AvailabilityAdminListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        return (
            ConsultantAvailability.objects
            .select_related("consultant")
            .order_by("-start_at")
        )

    def get_serializer_class(self):
        if self.request.method == "POST":
            return AvailabilityCreateSerializer

        return AvailabilitySerializer

    def perform_create(self, serializer):
        serializer.save()


class AvailabilityAdminDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ConsultantAvailability.objects.select_related("consultant")
    permission_classes = [IsAdminUser]
    serializer_class = AvailabilityCreateSerializer
