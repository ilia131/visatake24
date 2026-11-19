from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from apps.dashboard.selectors.appointments import (
    get_user_appointments,
)
from apps.dashboard.api.serializers.appointment import (
    DashboardAppointmentSerializer,
)


class DashboardAppointmentListAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = DashboardAppointmentSerializer

    def get_queryset(self):
        return get_user_appointments(self.request.user)