from __future__ import annotations

from dataclasses import dataclass

from django.db import transaction

from apps.countries.models import Country, CountryCurrency, Currency
from apps.countries.providers import CountryMetadataSnapshot


class CountrySnapshotValidationError(ValueError):
    pass


@dataclass(frozen=True)
class CountrySyncSummary:
    countries_created: int
    countries_updated: int
    currencies_created: int
    currencies_updated: int
    relationships_created: int
    relationships_updated: int
    dry_run: bool


def validate_full_snapshot(
    snapshots: tuple[CountryMetadataSnapshot, ...],
    *,
    minimum_countries: int = 200,
) -> None:
    if len(snapshots) < minimum_countries:
        raise CountrySnapshotValidationError(
            f"Country snapshot contains {len(snapshots)} records; expected at least {minimum_countries}"
        )
    iso2_codes = [snapshot.iso2 for snapshot in snapshots]
    iso3_codes = [snapshot.iso3 for snapshot in snapshots]
    if len(set(iso2_codes)) != len(iso2_codes) or len(set(iso3_codes)) != len(iso3_codes):
        raise CountrySnapshotValidationError("Country snapshot contains duplicate canonical codes")


def sync_country_metadata(
    snapshots: tuple[CountryMetadataSnapshot, ...],
    *,
    dry_run: bool = False,
    minimum_countries: int = 200,
) -> CountrySyncSummary:
    validate_full_snapshot(snapshots, minimum_countries=minimum_countries)

    counts = {
        "countries_created": 0,
        "countries_updated": 0,
        "currencies_created": 0,
        "currencies_updated": 0,
        "relationships_created": 0,
        "relationships_updated": 0,
    }

    with transaction.atomic():
        for snapshot in snapshots:
            country, created = Country.objects.update_or_create(
                iso2=snapshot.iso2,
                defaults={
                    "iso3": snapshot.iso3,
                    "name": snapshot.name,
                    "official_name": snapshot.official_name,
                    "capital": snapshot.capital,
                    "region": snapshot.region,
                    "subregion": snapshot.subregion,
                    "flag_url": snapshot.flag_url,
                    "is_active": True,
                    "metadata_source": snapshot.source_version,
                    "metadata_fetched_at": snapshot.fetched_at,
                },
            )
            counts["countries_created" if created else "countries_updated"] += 1

            for currency_snapshot in snapshot.currencies:
                currency, currency_created = Currency.objects.update_or_create(
                    code=currency_snapshot.code,
                    defaults={
                        "name": currency_snapshot.name,
                        "symbol": currency_snapshot.symbol,
                        "minor_units": currency_snapshot.minor_units,
                        "is_active": True,
                    },
                )
                counts["currencies_created" if currency_created else "currencies_updated"] += 1
                relationship, relationship_created = CountryCurrency.objects.update_or_create(
                    country=country,
                    currency=currency,
                    valid_to__isnull=True,
                    defaults={
                        "is_primary": len(snapshot.currencies) == 1,
                        "source": snapshot.source_version,
                    },
                )
                counts[
                    "relationships_created" if relationship_created else "relationships_updated"
                ] += 1

        if dry_run:
            transaction.set_rollback(True)

    return CountrySyncSummary(**counts, dry_run=dry_run)
