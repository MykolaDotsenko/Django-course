from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from django.contrib.auth import get_user_model
from django.db import transaction

from apps.countries.models import Country, CountryCurrency, Currency
from apps.travel.models import FavouritePair

MAX_SYNC_FAVOURITES = 12
MAX_ACCOUNT_FAVOURITES = 50

_CURRENCY_RE = re.compile(r"^[A-Z]{3}$")
_COUNTRY_RE = re.compile(r"^[A-Z]{2}$")
_PAIR_KEYS = {
    "sourceCurrency",
    "destinationCurrency",
    "sourceCountry",
    "destinationCountry",
}


class FavouriteSyncError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class FavouriteSpec:
    source_currency: Currency
    destination_currency: Currency
    source_country: Country | None
    destination_country: Country | None

    @property
    def key(self) -> tuple[int, int, int | None, int | None]:
        return (
            self.source_currency.pk,
            self.destination_currency.pk,
            self.source_country.pk if self.source_country else None,
            self.destination_country.pk if self.destination_country else None,
        )


@dataclass(frozen=True, slots=True)
class SyncResult:
    favourites: tuple[FavouritePair, ...]
    created_count: int


def _currency_code(value: Any, field_name: str) -> str:
    if not isinstance(value, str):
        raise FavouriteSyncError(f"{field_name} must be a three-letter currency code.")
    code = value.strip().upper()
    if not _CURRENCY_RE.fullmatch(code):
        raise FavouriteSyncError(f"{field_name} must be a three-letter currency code.")
    return code


def _country_code(value: Any, field_name: str) -> str:
    if value == "":
        return ""
    if not isinstance(value, str):
        raise FavouriteSyncError(f"{field_name} must be empty or a two-letter country code.")
    code = value.strip().upper()
    if not _COUNTRY_RE.fullmatch(code):
        raise FavouriteSyncError(f"{field_name} must be empty or a two-letter country code.")
    return code


def _normalize_items(raw_items: Any) -> list[tuple[str, str, str, str]]:
    if not isinstance(raw_items, list):
        raise FavouriteSyncError("favourites must be a list.")
    if len(raw_items) > MAX_SYNC_FAVOURITES:
        raise FavouriteSyncError(
            f"At most {MAX_SYNC_FAVOURITES} favourites may be synced per request."
        )

    normalized: list[tuple[str, str, str, str]] = []
    seen: set[tuple[str, str, str, str]] = set()
    for index, item in enumerate(raw_items):
        if not isinstance(item, dict) or set(item) != _PAIR_KEYS:
            raise FavouriteSyncError(
                f"Favourite {index + 1} must contain only the four pair identity fields."
            )
        pair = (
            _currency_code(item["sourceCurrency"], "sourceCurrency"),
            _currency_code(item["destinationCurrency"], "destinationCurrency"),
            _country_code(item["sourceCountry"], "sourceCountry"),
            _country_code(item["destinationCountry"], "destinationCountry"),
        )
        if pair not in seen:
            seen.add(pair)
            normalized.append(pair)
    return normalized


def _resolve_specs(raw_items: Any) -> list[FavouriteSpec]:
    normalized = _normalize_items(raw_items)
    currency_codes = {code for pair in normalized for code in pair[:2]}
    country_codes = {code for pair in normalized for code in pair[2:] if code}

    currencies = Currency.objects.in_bulk(currency_codes, field_name="code")
    countries = Country.objects.in_bulk(country_codes, field_name="iso2")

    missing_currencies = sorted(currency_codes - set(currencies))
    if missing_currencies:
        raise FavouriteSyncError(
            f"Unknown currency code: {', '.join(missing_currencies)}."
        )
    missing_countries = sorted(country_codes - set(countries))
    if missing_countries:
        raise FavouriteSyncError(
            f"Unknown country code: {', '.join(missing_countries)}."
        )

    required_associations = {
        (country_code, currency_code)
        for source_currency, destination_currency, source_country, destination_country in normalized
        for country_code, currency_code in (
            (source_country, source_currency),
            (destination_country, destination_currency),
        )
        if country_code
    }
    valid_associations = set(
        CountryCurrency.objects.filter(
            country__iso2__in={country for country, _ in required_associations},
            currency__code__in={currency for _, currency in required_associations},
        ).values_list("country__iso2", "currency__code")
    )
    invalid_associations = sorted(required_associations - valid_associations)
    if invalid_associations:
        country_code, currency_code = invalid_associations[0]
        raise FavouriteSyncError(
            f"{currency_code} is not a known currency context for {country_code}."
        )

    return [
        FavouriteSpec(
            source_currency=currencies[source_currency],
            destination_currency=currencies[destination_currency],
            source_country=countries.get(source_country) if source_country else None,
            destination_country=(
                countries.get(destination_country) if destination_country else None
            ),
        )
        for source_currency, destination_currency, source_country, destination_country in normalized
    ]


def sync_user_favourites(user, raw_items: Any) -> SyncResult:
    if not user.is_authenticated:
        raise FavouriteSyncError("Authentication is required.")

    specs = _resolve_specs(raw_items)
    user_model = get_user_model()

    with transaction.atomic():
        user_model.objects.select_for_update().get(pk=user.pk)
        favourites = FavouritePair.objects.filter(user=user)
        existing_keys = set(
            favourites.values_list(
                "source_currency_id",
                "destination_currency_id",
                "source_country_id",
                "destination_country_id",
            )
        )
        missing_count = sum(spec.key not in existing_keys for spec in specs)
        if favourites.count() + missing_count > MAX_ACCOUNT_FAVOURITES:
            raise FavouriteSyncError(
                f"An account may store at most {MAX_ACCOUNT_FAVOURITES} saved pairs."
            )

        created_count = 0
        for spec in specs:
            _, created = FavouritePair.objects.get_or_create(
                user=user,
                source_currency=spec.source_currency,
                destination_currency=spec.destination_currency,
                source_country=spec.source_country,
                destination_country=spec.destination_country,
            )
            created_count += int(created)

    canonical = tuple(
        FavouritePair.objects.filter(user=user)
        .select_related(
            "source_currency",
            "destination_currency",
            "source_country",
            "destination_country",
        )
        .order_by("-updated_at", "-id")
    )
    return SyncResult(favourites=canonical, created_count=created_count)


def serialize_favourite(favourite: FavouritePair) -> dict[str, str | int]:
    return {
        "id": favourite.pk,
        "sourceCurrency": favourite.source_currency.code,
        "destinationCurrency": favourite.destination_currency.code,
        "sourceCountry": favourite.source_country.iso2 if favourite.source_country else "",
        "destinationCountry": (
            favourite.destination_country.iso2 if favourite.destination_country else ""
        ),
        "sourceCountryName": favourite.source_country.name if favourite.source_country else "",
        "destinationCountryName": (
            favourite.destination_country.name if favourite.destination_country else ""
        ),
        "savedAt": favourite.created_at.isoformat(),
    }
