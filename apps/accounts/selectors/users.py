from django.contrib.auth import get_user_model

User = get_user_model()


def get_user_by_phone(*, phone_number):

    return User.objects.filter(
        phone_number=phone_number
    ).first()


def get_active_user(*, user_id):

    return User.objects.filter(
        id=user_id,
        is_active=True
    ).first()