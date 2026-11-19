
from django.db import transaction

from apps.consultants.models import Consultant


@transaction.atomic
def create_consultant(*, validated_data):
    return Consultant.objects.create(**validated_data)


@transaction.atomic
def update_consultant(*, consultant, validated_data):
    for field, value in validated_data.items():
        setattr(consultant, field, value)

    consultant.save()
    return consultant
