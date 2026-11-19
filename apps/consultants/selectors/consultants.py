
from django.db.models import QuerySet

from apps.consultants.models import Consultant


def get_public_consultants() -> QuerySet:
    return (
        Consultant.objects
        .filter(is_active=True, is_verified=True)
        .prefetch_related("specialties")
        .order_by("display_order", "-created_at")
    )


def get_consultant_by_slug(slug: str) -> Consultant | None:
    return (
        get_public_consultants()
        .filter(slug=slug)
        .first()
    )


def get_all_consultants():
    return (
        Consultant.objects
        .select_related("user")
        .prefetch_related("specialties")
        .order_by("display_order", "-created_at")
    )
