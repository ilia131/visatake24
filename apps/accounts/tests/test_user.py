from django.contrib.auth import get_user_model
import pytest


@pytest.mark.django_db
def test_create_user():
    User = get_user_model()

    user = User.objects.create_user(
        phone_number="+989121234567",
        password="StrongPassword123"
    )

    assert user.phone_number == "+989121234567"
    assert user.check_password("StrongPassword123")
    assert user.is_active is True


@pytest.mark.django_db
def test_create_superuser():
    User = get_user_model()

    admin = User.objects.create_superuser(
        phone_number="+989121234568",
        password="StrongPassword123"
    )

    assert admin.is_staff is True
    assert admin.is_superuser is True