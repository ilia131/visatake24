from apps.appointments.models import Appointment


def appointment_details():
    return Appointment.objects.select_related("user", "availability__consultant")


def get_user_appointments(*, user):
    return appointment_details().filter(user_id=user.pk)


def get_consultant_appointments(*, user):
    return appointment_details().filter(availability__consultant__user_id=user.pk)


def get_payment_appointments():
    return appointment_details().exclude(payment_receipt="")
