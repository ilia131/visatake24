
from django.db import transaction
from rest_framework.exceptions import ValidationError, NotFound

from apps.consultants.models import Consultant, ConsultantAssignment
from apps.visas.models import VisaApplication


@transaction.atomic
def assign_application(*, application_id, consultant_id, admin):
    try:
        application = (
            VisaApplication.objects
            .select_for_update()
            .get(pk=application_id)
        )
    except VisaApplication.DoesNotExist:
        raise NotFound("پرونده موردنظر پیدا نشد.")

    try:
        consultant = Consultant.objects.get(
            pk=consultant_id,
            is_active=True,
            is_verified=True,
        )
    except Consultant.DoesNotExist:
        raise NotFound("مشاور فعال و تأییدشده پیدا نشد.")

    current = (
        ConsultantAssignment.objects
        .select_for_update()
        .filter(application=application, is_active=True)
        .first()
    )

    if current and current.consultant_id == consultant.id:
        raise ValidationError("این پرونده قبلاً به همین مشاور ارجاع شده است.")

    if current:
        current.is_active = False
        current.save(update_fields=["is_active", "updated_at"])

    return ConsultantAssignment.objects.create(
        application=application,
        consultant=consultant,
        assigned_by=admin,
    )


@transaction.atomic
def update_assignment_status(
    *,
    assignment_id,
    consultant,
    status,
    consultant_note="",
):
    try:
        assignment = (
            ConsultantAssignment.objects
            .select_for_update()
            .get(
                pk=assignment_id,
                consultant=consultant,
                is_active=True,
            )
        )
    except ConsultantAssignment.DoesNotExist:
        raise NotFound("پرونده ارجاع‌شده پیدا نشد.")

    allowed_statuses = {
        ConsultantAssignment.Status.ASSIGNED,
        ConsultantAssignment.Status.IN_PROGRESS,
        ConsultantAssignment.Status.NEEDS_DOCUMENTS,
        ConsultantAssignment.Status.COMPLETED,
        ConsultantAssignment.Status.REJECTED,
    }

    if status not in allowed_statuses:
        raise ValidationError({"status": "وضعیت انتخاب‌شده معتبر نیست."})

    assignment.status = status
    assignment.consultant_note = consultant_note
    assignment.save(
        update_fields=["status", "consultant_note", "updated_at"]
    )

    return assignment
