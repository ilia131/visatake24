from apps.visas.models import Country, VisaApplication


def get_active_countries():

    return Country.objects.filter(
        is_active=True
    ).order_by("name")


def get_user_applications(user):

    return (
        VisaApplication.objects
        .filter(user=user)
        .select_related("country")
        .order_by("-created_at")
    )


def get_application_by_tracking_code(tracking_code, user):

    return (
        VisaApplication.objects
        .filter(
            tracking_code=tracking_code,
            user=user,
        )
        .select_related("country")
        .first()
    )