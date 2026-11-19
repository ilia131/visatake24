from django.db.models import Count
from django.utils import timezone

from apps.visas.models import VisaApplication
from apps.appointments.models import Appointment


def get_user_dashboard_overview(user):
    applications = VisaApplication.objects.filter(user=user)
    appointments = Appointment.objects.filter(user=user)

    status_counts = {
        item["status"]: item["total"]
        for item in applications.values("status").annotate(
            total=Count("id")
        )
    }

    now = timezone.now()

    return {
        "total_applications": applications.count(),
        "active_applications": applications.exclude(
            status__in=[
                VisaApplication.Status.COMPLETED,
                VisaApplication.Status.REJECTED,
            ]
        ).count(),
        "status_counts": status_counts,
        "total_appointments": appointments.count(),
        "upcoming_appointments": appointments.filter(
            status__in=[
                Appointment.Status.PENDING,
                Appointment.Status.CONFIRMED,
            ],
            availability__start_at__gte=now,
        ).count(),
    }