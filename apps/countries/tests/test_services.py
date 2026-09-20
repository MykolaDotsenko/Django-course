from datetime import UTC, datetime

import pytest

from apps.countries.models import Country
from apps.countries.providers import CountryMetadataSnapshot, CurrencySnapshot
from apps.countries.services import (
    CountrySnapshotValidationError,
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
def test_dry_run_reports_changes_without_persisting_them():
    summary = sync_country_metadata((snapshot(),), dry_run=True, minimum_countries=1)

    assert summary.dry_run is True
    assert summary.countries_created == 1
    assert not Country.objects.filter(iso2="FI").exists()
