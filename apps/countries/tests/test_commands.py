from io import StringIO
from unittest.mock import patch

from django.core.management import call_command

from apps.countries.services import CountrySyncSummary


def test_sync_country_metadata_command_surfaces_non_destructive_reconciliation_warning(monkeypatch):
    monkeypatch.setenv("REST_COUNTRIES_API_KEY", "test-key")
    summary = CountrySyncSummary(
        countries_created=0,
        countries_updated=250,
        currencies_created=0,
        currencies_updated=180,
        relationships_created=0,
        relationships_updated=250,
        missing_source_countries=("SE",),
        stale_source_relationships=("FI:USD",),
        dry_run=False,
    )
    stdout = StringIO()

    with (
        patch(
            "apps.countries.management.commands.sync_country_metadata.RestCountriesV5Client.fetch_all",
            return_value=(),
        ),
        patch(
            "apps.countries.management.commands.sync_country_metadata.sync_country_metadata",
            return_value=summary,
        ),
    ):
        call_command("sync_country_metadata", stdout=stdout)

    output = stdout.getvalue()
    assert "APPLIED:" in output
    assert "REVIEW REQUIRED:" in output
    assert "source-owned countries absent from snapshot=SE" in output
    assert "source-owned current relationships absent from snapshot=FI:USD" in output
    assert "No records were deactivated or deleted automatically." in output
