
from django.db import transaction
from rest_framework.exceptions import NotFound, ValidationError

from apps.visas.models import (
    VisaApplication,
    VisaApplicationStatusHistory,
)


@transaction.atomic
def create_visa_application(*, user, **validated_data):
    return VisaApplication.objects.create(
        user=user,
        **validated_data
    )


@transaction.atomic
def update_application_status(
    *,
    application,
    status,
    changed_by,
    admin_notes="",
):
    try:
        locked_application = (
            VisaApplication.objects
            .select_for_update()
            .get(pk=application.pk)
        )
    except VisaApplication.DoesNotExist:
        raise NotFound("پرونده پیدا نشد.")

    if status not in VisaApplication.Status.values:
        raise ValidationError({"status": "وضعیت انتخاب‌شده معتبر نیست."})

    previous_status = locked_application.status

    if admin_notes:
        locked_application.admin_notes = admin_notes

    if previous_status != status:
        locked_application.status = status

        VisaApplicationStatusHistory.objects.create(
            application=locked_application,
            previous_status=previous_status,
            new_status=status,
            changed_by=changed_by,
            note=admin_notes,
        )

    update_fields = ["admin_notes", "updated_at"]

    if previous_status != status:
        update_fields.append("status")

    locked_application.save(update_fields=update_fields)

    return locked_application
