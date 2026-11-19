
from apps.visas.services.applications import update_application_status


def change_application_status(
    *,
    application_id,
    new_status,
    user=None,
    description="",
):
    from apps.visas.models import VisaApplication
    from rest_framework.exceptions import NotFound

    try:
        application = VisaApplication.objects.get(pk=application_id)
    except VisaApplication.DoesNotExist:
        raise NotFound("پرونده پیدا نشد.")

    return update_application_status(
        application=application,
        status=new_status,
        changed_by=user,
        admin_notes=description,
    )
