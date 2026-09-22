from io import StringIO
from unittest.mock import Mock, patch

import pytest
from django.core.management import CommandError, call_command

from apps.exchange.metadata import (
    CurrencyCoverageSnapshotValidationError,
    CurrencyCoverageSyncSummary,
)
from apps.exchange.providers.frankfurter_metadata import FrankfurterMetadataError


def test_sync_fx_currency_coverage_command_reports_applied_summary():
    client = Mock()
    client.fetch_currency_coverage.return_value = ()
    summary = CurrencyCoverageSyncSummary(
        currencies_created=3,
        currencies_updated=5,
        currencies_unchanged=7,
        dry_run=False,
    )
    stdout = StringIO()

    with (
        patch(
            "apps.exchange.management.commands.sync_fx_currency_coverage.FrankfurterMetadataClient",
            return_value=client,
        ) as client_factory,
        patch(
            "apps.exchange.management.commands.sync_fx_currency_coverage.sync_currency_coverage",
            return_value=summary,
        ) as sync,
    ):
        call_command(
            "sync_fx_currency_coverage",
            base_url="https://fx.example.test/v2",
            stdout=stdout,
        )

    client_factory.assert_called_once_with(base_url="https://fx.example.test/v2")
    client.fetch_currency_coverage.assert_called_once_with()
    sync.assert_called_once_with((), dry_run=False)
    assert "APPLIED: currencies +3/~5/=7" in stdout.getvalue()


def test_sync_fx_currency_coverage_command_propagates_dry_run_to_service():
    client = Mock()
    client.fetch_currency_coverage.return_value = ()
    summary = CurrencyCoverageSyncSummary(
        currencies_created=1,
        currencies_updated=0,
        currencies_unchanged=0,
        dry_run=True,
    )
    stdout = StringIO()

    with (
        patch(
            "apps.exchange.management.commands.sync_fx_currency_coverage.FrankfurterMetadataClient",
            return_value=client,
        ),
        patch(
            "apps.exchange.management.commands.sync_fx_currency_coverage.sync_currency_coverage",
            return_value=summary,
        ) as sync,
    ):
        call_command("sync_fx_currency_coverage", dry_run=True, stdout=stdout)

    sync.assert_called_once_with((), dry_run=True)
    assert "DRY RUN: currencies +1/~0/=0" in stdout.getvalue()


@pytest.mark.parametrize(
    "error",
    [
        FrankfurterMetadataError("provider unavailable"),
        CurrencyCoverageSnapshotValidationError("snapshot incomplete"),
        ValueError("invalid configuration"),
    ],
)
def test_sync_fx_currency_coverage_command_maps_expected_failures_to_command_error(error):
    client = Mock()
    client.fetch_currency_coverage.side_effect = error

    with (
        patch(
            "apps.exchange.management.commands.sync_fx_currency_coverage.FrankfurterMetadataClient",
            return_value=client,
        ),
        pytest.raises(CommandError, match=str(error)),
    ):
        call_command("sync_fx_currency_coverage")
