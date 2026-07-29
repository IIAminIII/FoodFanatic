import uuid

from django.conf import settings
from django.db import models


class AccountModel(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="account",
    )
    is_activated = models.BooleanField(default=False)
    email_token = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"Account settings for {self.user}"
