from django.conf import settings
from django.db import IntegrityError, transaction
from django.utils import timezone
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError

from apps.appointments.api.permissions import can_review_payment
from apps.appointments.models import Appointment, ConsultantAvailability
from apps.appointments.models.appointment import AppointmentHistory, OCCUPYING_STATUSES
from apps.appointments.services.notifications import queue_appointment_event

Status = Appointment.Status

TRANSITIONS = {
    "consultant_approve": ((Status.PENDING,), Status.AWAITING_PAYMENT),
    "consultant_reject": ((Status.PENDING,), Status.REJECTED),
    "submit_receipt": ((Status.AWAITING_PAYMENT, Status.PAYMENT_REJECTED), Status.PAYMENT_SUBMITTED),
    "payment_approve": ((Status.PAYMENT_SUBMITTED,), Status.CONFIRMED),
    "payment_reject": ((Status.PAYMENT_SUBMITTED,), Status.PAYMENT_REJECTED),
    "cancel": ((Status.PENDING, Status.CONFIRMED), Status.CANCELLED),
    "complete": ((Status.CONFIRMED,), Status.COMPLETED),
}


def _record_change(appointment, previous, actor, note=""):
    AppointmentHistory.objects.create(
        appointment=appointment,
        previous_status=previous,
        new_status=appointment.status,
        changed_by=actor,
        note=note,
    )
    queue_appointment_event(appointment_id=appointment.pk, event=appointment.status)


def _require_valid_slot(availability, now):
    if availability.start_at <= now:
        raise ValidationError({"availability": "این زمان گذشته است."})
    consultant = availability.consultant
    if availability.status != ConsultantAvailability.Status.AVAILABLE or not (
        consultant.is_active and consultant.is_verified
    ):
        raise NotFound("زمان مشاوره پیدا نشد.")


def _require_unoccupied(availability, *, exclude=None):
    if Appointment.objects.filter(
        availability=availability, status__in=OCCUPYING_STATUSES,
    ).exclude(pk=exclude).exists():
        raise ValidationError({"availability": "این زمان قبلاً رزرو شده است."})


def _save_booking(appointment, **kwargs):
    try:
        with transaction.atomic():
            appointment.save(**kwargs)
    except IntegrityError as exc:
        cause = exc.__cause__
        constraint = getattr(getattr(cause, "diag", None), "constraint_name", None)
        if constraint == "unique_active_appointment_per_slot" or (
            str(cause) == "UNIQUE constraint failed: appointments_appointment.availability_id"
        ):
            raise ValidationError({"availability": "این زمان قبلاً رزرو شده است."}) from exc
        raise


@transaction.atomic
def book_appointment(*, user, availability_id, user_note=""):
    availability = _locked_slot(availability_id)
    _require_valid_slot(availability, timezone.now())
    _require_unoccupied(availability)
    appointment = Appointment(
        user=user, availability=availability, user_note=user_note,
        consultation_fee=availability.consultant.consultation_fee,
    )
    _save_booking(appointment, force_insert=True)
    _record_change(appointment, "", user, user_note)
    return appointment


def _locked_slot(pk):
    try:
        return ConsultantAvailability.objects.select_related("consultant").select_for_update(
            of=("self",),
        ).get(pk=pk)
    except ConsultantAvailability.DoesNotExist as exc:
        raise NotFound("زمان مشاوره پیدا نشد.") from exc


def _check_actor(appointment, action, actor):
    if action.startswith("payment_"):
        if not can_review_payment(actor):
            raise PermissionDenied()
    elif action.startswith("consultant_") or action == "complete":
        if appointment.availability.consultant.user_id != actor.pk:
            raise NotFound("رزرو موردنظر پیدا نشد.")
    elif appointment.user_id != actor.pk:
        raise NotFound("رزرو موردنظر پیدا نشد.")


def change_appointment(*, appointment_id, actor, action, note="", receipt=None):
    allowed, target = TRANSITIONS[action]
    stored_receipt = None
    try:
        with transaction.atomic():
            # Every writer locks the slot before taking the appointment lock.
            slot_id = Appointment.objects.filter(pk=appointment_id).values_list(
                "availability_id", flat=True,
            ).first()
            if slot_id is None:
                raise NotFound("رزرو موردنظر پیدا نشد.")
            availability = _locked_slot(slot_id)
            appointment = Appointment.objects.select_for_update().filter(
                pk=appointment_id, availability=availability,
            ).first()
            if appointment is None:
                raise NotFound("رزرو موردنظر پیدا نشد.")
            appointment.availability = availability
            _check_actor(appointment, action, actor)

            previous = appointment.status
            if previous not in allowed:
                raise ValidationError("این عملیات در وضعیت فعلی رزرو مجاز نیست.")

            now = timezone.now()
            if action in {"consultant_approve", "submit_receipt", "payment_approve"}:
                _require_valid_slot(availability, now)
            if action == "complete" and now < availability.end_at:
                raise ValidationError("جلسه هنوز پایان نیافته است.")

            if action == "consultant_approve":
                if not settings.APPOINTMENT_PAYMENT_CARD:
                    raise ValidationError("شماره کارت پرداخت هنوز تنظیم نشده است.")
                appointment.consultant_approved_at = now
            elif action == "consultant_reject":
                appointment.rejection_reason = note
            elif action == "submit_receipt":
                _require_unoccupied(availability, exclude=appointment.pk)
                old_name = appointment.payment_receipt.name
                appointment.payment_receipt.save(receipt.name, receipt, save=False)
                stored_receipt = appointment.payment_receipt
                if old_name:
                    transaction.on_commit(
                        lambda: stored_receipt.storage.delete(old_name), robust=True,
                    )
                appointment.payment_submitted_at = now
                appointment.payment_reviewed_at = None
                appointment.payment_reviewed_by = None
                appointment.payment_note = ""
            elif action.startswith("payment_"):
                appointment.payment_reviewed_by = actor
                appointment.payment_reviewed_at = now
                appointment.payment_note = note
                if action == "payment_approve":
                    appointment.confirmed_at = now

            appointment.status = target
            _save_booking(appointment)
            _record_change(appointment, previous, actor, note)
    except Exception:
        if stored_receipt:
            stored_receipt.delete(save=False)
        raise

    return appointment


def cancel_appointment(*, appointment_id, user):
    return change_appointment(appointment_id=appointment_id, actor=user, action="cancel")
