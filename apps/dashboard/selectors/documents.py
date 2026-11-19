from apps.visas.models import VisaApplicationDocument


def get_user_documents(user):
    return (
        VisaApplicationDocument.objects
        .filter(application__user=user)
        .select_related("application")
        .order_by("-uploaded_at")
    )