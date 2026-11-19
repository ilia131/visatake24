from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.accounts.managers import UserManager


class User(AbstractUser):

    class Role(models.TextChoices):
        CUSTOMER = "customer", "Customer"
        AGENT = "agent", "Agent"
        MANAGER = "manager", "Manager"

    username = None

    phone_number = models.CharField(
        max_length=16,
        unique=True,
        db_index=True,
        verbose_name="شماره موبایل",
    )

    email = models.EmailField(
        blank=True,
        null=True,
        verbose_name="ایمیل",
    )

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CUSTOMER,
    )

    is_phone_verified = models.BooleanField(
        default=False,
        verbose_name="تأیید شماره موبایل",
    )

    USERNAME_FIELD = "phone_number"

    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        db_table = "accounts_user"
        ordering = ["-date_joined"]

    def __str__(self):
        return self.phone_number