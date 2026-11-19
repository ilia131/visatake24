
from rest_framework import generics
from rest_framework.permissions import AllowAny

from apps.appointments.api.serializers.availability import (
    AvailabilitySerializer,
)
from apps.appointments.selectors.availability import (
    get_available_slots,
)


class AvailabilityListAPIView(generics.ListAPIView):
    serializer_class = AvailabilitySerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        consultant_id = self.request.query_params.get("consultant")
        return get_available_slots(consultant_id=consultant_id)


class AvailabilityDetailAPIView(generics.RetrieveAPIView):
    serializer_class = AvailabilitySerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return get_available_slots()
