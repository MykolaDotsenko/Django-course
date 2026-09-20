from __future__ import annotations

from dataclasses import dataclass

from django.db import transaction

from apps.countries.models import Currency
from apps.exchange.providers.frankfurter_metadata import FrankfurterCurrencyCoverageSnapshot


class CurrencyCoverageSnapshotValidationError(ValueError):
    pass


@dataclass(frozen=True)
class CurrencyCoverageSyncSummary:
    currencies_created: int
    currencies_updated: int
    currencies_unchanged: int
    dry_run: bool


def validate_currency_coverage_snapshot(
    snapshots: tuple[FrankfurterCurrencyCoverageSnapshot, ...],
    *,
    minimum_currencies: int = 150,
) -> None:
    if len(snapshots) < minimum_currencies:
        raise CurrencyCoverageSnapshotValidationError(
            f"FX currency coverage snapshot contains {len(snapshots)} records; "
            f"expected at least {minimum_currencies}."
        )
    codes = [snapshot.code for snapshot in snapshots]
    if len(set(codes)) != len(codes):
        raise CurrencyCoverageSnapshotValidationError(
            "FX currency coverage snapshot contains duplicate codes."
        )


def sync_currency_coverage(
    snapshots: tuple[FrankfurterCurrencyCoverageSnapshot, ...],
    *,
    dry_run: bool = False,
    minimum_currencies: int = 150,
) -> CurrencyCoverageSyncSummary:
    validate_currency_coverage_snapshot(snapshots, minimum_currencies=minimum_currencies)

    created = 0
    updated = 0
    unchanged = 0

    with transaction.atomic():
        for snapshot in snapshots:
            currency = Currency.objects.filter(code=snapshot.code).first()
            if currency is None:
                Currency.objects.create(
                    code=snapshot.code,
                    name=snapshot.name,
                    symbol=snapshot.symbol,
                    is_active=False,
                    coverage_from=snapshot.coverage_from,
                    coverage_to=snapshot.coverage_to,
                    coverage_to_is_terminal=snapshot.coverage_to_is_terminal,
                    coverage_source=snapshot.source_version,
                    coverage_fetched_at=snapshot.fetched_at,
                )
                created += 1
                continue

            changes = {
                "coverage_from": snapshot.coverage_from,
                "coverage_to": snapshot.coverage_to,
                "coverage_to_is_terminal": snapshot.coverage_to_is_terminal,
                "coverage_source": snapshot.source_version,
                "coverage_fetched_at": snapshot.fetched_at,
            }
            if not currency.name:
                changes["name"] = snapshot.name
            if not currency.symbol and snapshot.symbol:
                changes["symbol"] = snapshot.symbol

            dirty_fields = [
                field_name
                for field_name, value in changes.items()
                if getattr(currency, field_name) != value
            ]
            if not dirty_fields:
                unchanged += 1
                continue

            for field_name in dirty_fields:
                setattr(currency, field_name, changes[field_name])
            currency.save(update_fields=dirty_fields)
            updated += 1

        if dry_run:
            transaction.set_rollback(True)

    return CurrencyCoverageSyncSummary(
        currencies_created=created,
        currencies_updated=updated,
        currencies_unchanged=unchanged,
        dry_run=dry_run,
    )
