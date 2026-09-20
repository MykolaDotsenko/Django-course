import os

from django.core.management.base import BaseCommand, CommandError

from apps.exchange.metadata import (
    CurrencyCoverageSnapshotValidationError,
    sync_currency_coverage,
)
from apps.exchange.providers.frankfurter import DEFAULT_BASE_URL
from apps.exchange.providers.frankfurter_metadata import (
    FrankfurterMetadataClient,
    FrankfurterMetadataError,
)


class Command(BaseCommand):
    help = "Sync Frankfurter v2 currency provider coverage without rewriting currency lifecycle."

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true")
        parser.add_argument(
            "--base-url",
            default=os.environ.get("FRANKFURTER_BASE_URL", DEFAULT_BASE_URL),
        )

    def handle(self, *args, **options):
        client = FrankfurterMetadataClient(base_url=options["base_url"])
        try:
            snapshots = client.fetch_currency_coverage()
            summary = sync_currency_coverage(snapshots, dry_run=options["dry_run"])
        except (
            CurrencyCoverageSnapshotValidationError,
            FrankfurterMetadataError,
            ValueError,
        ) as exc:
            raise CommandError(str(exc)) from exc

        mode = "DRY RUN" if summary.dry_run else "APPLIED"
        self.stdout.write(
            self.style.SUCCESS(
                f"{mode}: currencies +{summary.currencies_created}/"
                f"~{summary.currencies_updated}/"
                f"={summary.currencies_unchanged}"
            )
        )
