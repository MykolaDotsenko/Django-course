from __future__ import annotations

from django.conf import settings
from django.db import models


class AccountPreferences(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="account_preferences",
    )
    sync_recent_history = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.user_id}: recent_history={self.sync_recent_history}"
