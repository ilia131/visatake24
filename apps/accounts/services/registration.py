from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()


@transaction.atomic
def register_user(*, phone_number):

    user = User.objects.create_user(
        phone_number=phone_number
    )

    return user