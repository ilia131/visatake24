from django.db import models


class AuthAttempt(models.Model):
    key = models.CharField(max_length=64, primary_key=True)
    window = models.BigIntegerField(db_index=True)
    count = models.PositiveIntegerField(default=0)
