from __future__ import annotations

from django.contrib.auth import get_user_model
from django.db import transaction

from apps.accounts.models import AccountPreferences


def recent_history_enabled(user) -> bool:
    return bool(
        user.is_authenticated
        and AccountPreferences.objects.filter(
            user=user,
            sync_recent_history=True,
        ).exists()
    )


def set_recent_history_enabled(user, *, enabled: bool) -> AccountPreferences:
    if not user.is_authenticated:
        raise ValueError("Authentication is required.")

    user_model = get_user_model()
    with transaction.atomic():
        user_model.objects.select_for_update().get(pk=user.pk)
        preferences, _ = AccountPreferences.objects.update_or_create(
            user=user,
            defaults={"sync_recent_history": enabled},
        )
    return preferences
