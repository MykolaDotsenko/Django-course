from __future__ import annotations

from datetime import date
from decimal import Decimal
from hashlib import sha256

from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from apps.accounts.models import AccountPreferences
from apps.countries.models import Country, Currency
from apps.travel.models import RecentConversion

MAX_ACCOUNT_RECENTS = 50


def _canonical_decimal(value: Decimal) -> str:
    text = format(value, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text or "0"


def _fingerprint(
    *,
    source_currency: str,
    destination_currency: str,
    source_country: str,
    destination_country: str,
    input_amount: str,
    rate_mode: str,
    requested_date: date | None,
) -> str:
    identity = "|".join(
        (
            source_country or "_",
            source_currency,
            destination_country or "_",
            destination_currency,
            input_amount,
            rate_mode,
            requested_date.isoformat() if requested_date is not None else "latest",
        )
    )
    return sha256(identity.encode("utf-8")).hexdigest()


def record_recent_conversion(
    user,
    *,
    source_currency_code: str,
    destination_currency_code: str,
    source_country_code: str,
    destination_country_code: str,
    input_amount: Decimal,
    output_amount: Decimal,
    historical: bool,
    requested_date: date | None,
    effective_date: date,
) -> RecentConversion | None:
    if not user.is_authenticated:
        return None
    if not AccountPreferences.objects.filter(
        user=user,
        sync_recent_history=True,
    ).exists():
        return None

    source_currency = Currency.objects.get(code=source_currency_code)
    destination_currency = Currency.objects.get(code=destination_currency_code)
    source_country = (
        Country.objects.filter(iso2=source_country_code).first() if source_country_code else None
    )
    destination_country = (
        Country.objects.filter(iso2=destination_country_code).first()
        if destination_country_code
        else None
    )
    input_text = format(input_amount, "f")
    output_text = format(output_amount, "f")
    fingerprint_input = _canonical_decimal(input_amount)
    rate_mode = (
        RecentConversion.RateMode.HISTORICAL if historical else RecentConversion.RateMode.LATEST
    )
    normalized_requested_date = requested_date if historical else None
    fingerprint = _fingerprint(
        source_currency=source_currency.code,
        destination_currency=destination_currency.code,
        source_country=source_country.iso2 if source_country else "",
        destination_country=destination_country.iso2 if destination_country else "",
        input_amount=fingerprint_input,
        rate_mode=rate_mode,
        requested_date=normalized_requested_date,
    )

    user_model = get_user_model()
    now = timezone.now()
    with transaction.atomic():
        user_model.objects.select_for_update().get(pk=user.pk)
        if not AccountPreferences.objects.filter(
            user=user,
            sync_recent_history=True,
        ).exists():
            return None

        recent, _ = RecentConversion.objects.update_or_create(
            user=user,
            fingerprint=fingerprint,
            defaults={
                "source_currency": source_currency,
                "destination_currency": destination_currency,
                "source_country": source_country,
                "destination_country": destination_country,
                "input_amount": input_text,
                "output_amount": output_text,
                "rate_mode": rate_mode,
                "requested_date": normalized_requested_date,
                "effective_date": effective_date,
                "converted_at": now,
            },
        )
        stale_ids = list(
            RecentConversion.objects.filter(user=user)
            .order_by("-converted_at", "-id")
            .values_list("id", flat=True)[MAX_ACCOUNT_RECENTS:]
        )
        if stale_ids:
            RecentConversion.objects.filter(user=user, id__in=stale_ids).delete()

    return recent
