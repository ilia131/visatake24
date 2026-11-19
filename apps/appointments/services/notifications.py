from django.db import transaction
from django.dispatch import Signal


# Receivers can route events to the relevant consultant, owner, or payment reviewer.
appointment_event = Signal()


def queue_appointment_event(*, appointment_id, event):
    transaction.on_commit(
        lambda: appointment_event.send_robust(
            sender=queue_appointment_event, appointment_id=appointment_id, event=event,
        )
    )


def remind_appointment(*, appointment_id):
    from apps.appointments.models import Appointment

    if Appointment.objects.filter(pk=appointment_id, status=Appointment.Status.CONFIRMED).exists():
        queue_appointment_event(appointment_id=appointment_id, event="reminder")
