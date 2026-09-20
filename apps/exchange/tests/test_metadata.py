from datetime import UTC, date, datetime

import pytest

from apps.countries.models import Currency
from apps.exchange.metadata import (
    CurrencyCoverageSnapshotValidationError,
    sync_currency_coverage,
    validate_currency_coverage_snapshot,
)
from apps.exchange.providers.frankfurter_metadata import (
    FrankfurterCurrencyCoverageSnapshot,
    FrankfurterMetadataError,
    build_currency_coverage_snapshots,
)

FETCHED_AT = datetime(2026, 9, 20, 12, tzinfo=UTC)


def snapshot(
    code: str,
    *,
    coverage_from: date | None = date(1999, 1, 4),
    coverage_to: date | None = date(2026, 9, 18),
    terminal: bool = False,
) -> FrankfurterCurrencyCoverageSnapshot:
    return FrankfurterCurrencyCoverageSnapshot(
        code=code,
        name={"EUR": "Euro", "FIM": "Finnish Markka"}.get(code, code),
        symbol={"EUR": "€", "FIM": "mk"}.get(code, ""),
        coverage_from=coverage_from,
        coverage_to=coverage_to,
        coverage_to_is_terminal=terminal,
        source_version="frankfurter-v2-currencies",
        fetched_at=FETCHED_AT,
    )

def test_currency_metadata_distinguishes_active_latest_observation_from_terminal_legacy_end():
    active = [
        {
            "iso_code": "EUR",
            "name": "Euro",
            "symbol": "€",
            "start_date": "1999-01-04",
            "end_date": "2026-09-18",
        }
    ]
    all_rows = [
        *active,
        {
            "iso_code": "FIM",
            "name": "Finnish Markka",
            "symbol": "mk",
            "start_date": "1972-01-03",
            "end_date": "2001-12-28",
        },
    ]

    result = build_currency_coverage_snapshots(active, all_rows, fetched_at=FETCHED_AT)

    by_code = {item.code: item for item in result}
    assert by_code["EUR"].coverage_to == date(2026, 9, 18)
    assert by_code["EUR"].coverage_to_is_terminal is False
    assert by_code["FIM"].coverage_to == date(2001, 12, 28)
    assert by_code["FIM"].coverage_to_is_terminal is True

def test_currency_metadata_rejects_active_set_missing_from_scope_all():
    with pytest.raises(FrankfurterMetadataError, match="subset"):
        build_currency_coverage_snapshots(
            [{"iso_code": "EUR", "name": "Euro"}],
            [{"iso_code": "USD", "name": "United States Dollar"}],
            fetched_at=FETCHED_AT,
        )

def test_currency_metadata_rejects_reversed_coverage():
    with pytest.raises(FrankfurterMetadataError, match="reversed"):
        build_currency_coverage_snapshots(
            [],
            [
                {
                    "iso_code": "FIM",
                    "name": "Finnish Markka",
                    "start_date": "2002-01-01",
                    "end_date": "2001-12-31",
                }
            ],
            fetched_at=FETCHED_AT,
        )

def test_coverage_snapshot_validation_rejects_suspiciously_small_import():
    with pytest.raises(CurrencyCoverageSnapshotValidationError):
        validate_currency_coverage_snapshot((snapshot("EUR"),), minimum_currencies=150)

@pytest.mark.django_db
def test_coverage_sync_preserves_currency_lifecycle_and_current_status():
    currency = Currency.objects.create(
        code="EUR",
        name="Euro",
        symbol="€",
        is_active=True,
        active_from=date(2002, 1, 1),
    )

    summary = sync_currency_coverage((snapshot("EUR"),), minimum_currencies=1)

    currency.refresh_from_db()
    assert summary.currencies_updated == 1
    assert currency.is_active is True
    assert currency.active_from == date(2002, 1, 1)
    assert currency.active_to is None
    assert currency.coverage_from == date(1999, 1, 4)
    assert currency.coverage_to == date(2026, 9, 18)
    assert currency.coverage_to_is_terminal is False
    assert currency.coverage_source == "frankfurter-v2-currencies"
    assert currency.coverage_fetched_at == FETCHED_AT

@pytest.mark.django_db
def test_coverage_sync_creates_provider_only_currency_as_historical_only():
    summary = sync_currency_coverage(
        (
            snapshot(
                "FIM",
                coverage_from=date(1972, 1, 3),
                coverage_to=date(2001, 12, 28),
                terminal=True,
            ),
        ),
        minimum_currencies=1,
    )

    fim = Currency.objects.get(code="FIM")
    assert summary.currencies_created == 1
    assert fim.is_active is False
    assert fim.active_from is None
    assert fim.active_to is None
    assert fim.coverage_to_is_terminal is True

@pytest.mark.django_db
def test_coverage_sync_dry_run_reports_without_persisting():
    summary = sync_currency_coverage(
        (snapshot("FIM", terminal=True),),
        dry_run=True,
        minimum_currencies=1,
    )

    assert summary.dry_run is True
    assert summary.currencies_created == 1
    assert not Currency.objects.filter(code="FIM").exists()


@pytest.mark.django_db
def test_coverage_sync_is_idempotent_for_identical_snapshot():
    records = (snapshot("EUR"),)

    first = sync_currency_coverage(records, minimum_currencies=1)
    second = sync_currency_coverage(records, minimum_currencies=1)

    assert first.currencies_created == 1
    assert second.currencies_created == 0
    assert second.currencies_updated == 0
    assert second.currencies_unchanged == 1
