from datetime import UTC, date, datetime

import pytest

from apps.countries.models import Country, CountryCurrency, Currency
from apps.countries.providers import CountryMetadataSnapshot, CurrencySnapshot
from apps.countries.services import (
    CountrySnapshotValidationError,
    historical_currency_suggestion,
    sync_country_metadata,
    validate_full_snapshot,
)


def snapshot(iso2="FI", iso3="FIN", name="Finland"):
    return CountryMetadataSnapshot(
        iso2=iso2,
        iso3=iso3,
        name=name,
        official_name=name,
        capital="Helsinki",
        region="Europe",
        subregion="Northern Europe",
        flag_url="",
        currencies=(CurrencySnapshot("EUR", "Euro", "€", 2),),
        source_version="rest-countries-v5",
        fetched_at=datetime(2026, 9, 20, tzinfo=UTC),
    )


def test_full_snapshot_rejects_suspiciously_small_response():
    with pytest.raises(CountrySnapshotValidationError):
        validate_full_snapshot((snapshot(),), minimum_countries=200)


@pytest.mark.django_db
def test_sync_is_idempotent_and_does_not_delete_unmentioned_rows():
    existing = Country.objects.create(iso2="ZZ", iso3="ZZZ", name="Existing")
    records = (snapshot(),)

    first = sync_country_metadata(records, minimum_countries=1)
    second = sync_country_metadata(records, minimum_countries=1)

    assert first.countries_created == 1
    assert second.countries_created == 0
    assert Country.objects.filter(pk=existing.pk).exists()


@pytest.mark.django_db
def test_sync_reports_source_owned_country_missing_from_full_snapshot_without_deleting_it():
    missing = Country.objects.create(
        iso2="SE",
        iso3="SWE",
        name="Sweden",
        metadata_source="rest-countries-v5",
    )

    summary = sync_country_metadata((snapshot(),), minimum_countries=1)

    assert summary.requires_reconciliation_review is True
    assert summary.missing_source_countries == ("SE",)
    assert summary.stale_source_relationships == ()
    assert Country.objects.filter(pk=missing.pk, is_active=True).exists()


@pytest.mark.django_db
def test_sync_reports_stale_source_owned_current_relationship_without_closing_it():
    finland = Country.objects.create(
        iso2="FI",
        iso3="FIN",
        name="Finland",
        metadata_source="rest-countries-v5",
    )
    eur = Currency.objects.create(code="EUR", name="Euro")
    usd = Currency.objects.create(code="USD", name="US dollar")
    stale = CountryCurrency.objects.create(
        country=finland,
        currency=usd,
        is_primary=False,
        source="rest-countries-v5",
    )
    CountryCurrency.objects.create(
        country=finland,
        currency=eur,
        is_primary=True,
        source="rest-countries-v5",
    )

    summary = sync_country_metadata((snapshot(),), minimum_countries=1)

    assert summary.requires_reconciliation_review is True
    assert summary.missing_source_countries == ()
    assert summary.stale_source_relationships == ("FI:USD",)
    stale.refresh_from_db()
    assert stale.valid_to is None


@pytest.mark.django_db
def test_sync_does_not_report_rows_owned_by_other_sources_as_snapshot_drift():
    country = Country.objects.create(
        iso2="SE",
        iso3="SWE",
        name="Sweden",
        metadata_source="curated-manual",
    )
    sek = Currency.objects.create(code="SEK", name="Swedish krona")
    CountryCurrency.objects.create(
        country=country,
        currency=sek,
        is_primary=True,
        source="curated-history-v1",
    )

    summary = sync_country_metadata((snapshot(),), minimum_countries=1)

    assert summary.requires_reconciliation_review is False
    assert summary.missing_source_countries == ()
    assert summary.stale_source_relationships == ()


@pytest.mark.django_db
def test_dry_run_reports_changes_without_persisting_them():
    summary = sync_country_metadata((snapshot(),), dry_run=True, minimum_countries=1)

    assert summary.dry_run is True
    assert summary.countries_created == 1
    assert not Country.objects.filter(iso2="FI").exists()


@pytest.mark.django_db
def test_historical_currency_suggestion_preserves_explicit_user_choice():
    finland = Country.objects.create(iso2="FI", iso3="FIN", name="Finland")
    eur = Currency.objects.create(code="EUR", name="Euro")
    fim = Currency.objects.create(code="FIM", name="Finnish markka", is_active=False)
    CountryCurrency.objects.create(
        country=finland,
        currency=fim,
        is_primary=True,
        valid_to=date(2001, 12, 31),
        source="curated-history-v1",
    )
    CountryCurrency.objects.create(
        country=finland,
        currency=eur,
        is_primary=True,
        valid_from=date(2002, 1, 1),
        source="curated-history-v1",
    )

    suggestion = historical_currency_suggestion(
        country_code="FI",
        selected_currency_code="EUR",
        selected_date=date(1998, 6, 15),
    )

    assert suggestion is not None
    assert suggestion.selected_currency_code == "EUR"
    assert suggestion.suggested_currency_code == "FIM"
    assert suggestion.source == "curated-history-v1"


@pytest.mark.django_db
def test_historical_currency_suggestion_is_none_when_selection_matches_era():
    finland = Country.objects.create(iso2="FI", iso3="FIN", name="Finland")
    fim = Currency.objects.create(code="FIM", name="Finnish markka", is_active=False)
    CountryCurrency.objects.create(
        country=finland,
        currency=fim,
        is_primary=True,
        valid_to=date(2001, 12, 31),
        source="curated-history-v1",
    )

    assert (
        historical_currency_suggestion(
            country_code="FI",
            selected_currency_code="FIM",
            selected_date=date(1998, 6, 15),
        )
        is None
    )
