
from django.utils import timezone
from django.db.models import Exists, OuterRef

from apps.appointments.models import Appointment, ConsultantAvailability
from apps.appointments.models.appointment import OCCUPYING_STATUSES


def get_available_slots(*, consultant_id=None):
    now = timezone.now()

    active_bookings = Appointment.objects.filter(
        availability_id=OuterRef("pk"),
        status__in=OCCUPYING_STATUSES,
    )

    queryset = (
        ConsultantAvailability.objects
        .filter(
            status=ConsultantAvailability.Status.AVAILABLE,
            end_at__gt=now,
            consultant__is_active=True,
            consultant__is_verified=True,
        )
        .annotate(is_booked=Exists(active_bookings))
        .filter(is_booked=False)
        .select_related("consultant")
        .order_by("start_at")
    )

    if consultant_id:
        queryset = queryset.filter(consultant_id=consultant_id)

    return queryset
