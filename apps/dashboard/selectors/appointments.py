from apps.appointments.models import Appointment


def get_user_appointments(user):
    return (
        Appointment.objects
        .filter(user=user)
        .select_related(
            "availability",
            "availability__consultant",
        )
        .order_by("-availability__start_at")
    )