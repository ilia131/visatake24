from apps.visas.models import VisaApplication


def get_user_applications(user):
    return (
        VisaApplication.objects
        .filter(user=user)
        .select_related("country")
        .prefetch_related("status_history")
        .order_by("-created_at")
    )


def get_user_application_detail(user, tracking_code):
    return (
        get_user_applications(user)
        .filter(tracking_code=tracking_code)
        .first()
    )