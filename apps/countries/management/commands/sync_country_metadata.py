import os

from django.core.management.base import BaseCommand, CommandError

from apps.countries.providers import REST_COUNTRIES_V5_BASE_URL, RestCountriesV5Client
from apps.countries.services import CountrySnapshotValidationError, sync_country_metadata


class Command(BaseCommand):
    help = "Import selected current country/currency metadata from REST Countries v5."

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true")
        parser.add_argument(
            "--base-url",
            default=os.environ.get("REST_COUNTRIES_BASE_URL", REST_COUNTRIES_V5_BASE_URL),
        )

    def handle(self, *args, **options):
        api_key = os.environ.get("REST_COUNTRIES_API_KEY", "").strip()
        if not api_key:
            raise CommandError("REST_COUNTRIES_API_KEY is required for this import")

        client = RestCountriesV5Client(api_key=api_key, base_url=options["base_url"])
        try:
            snapshots = client.fetch_all()
            summary = sync_country_metadata(snapshots, dry_run=options["dry_run"])
        except (CountrySnapshotValidationError, RuntimeError, ValueError) as exc:
            raise CommandError(str(exc)) from exc

        mode = "DRY RUN" if summary.dry_run else "APPLIED"
        self.stdout.write(
            self.style.SUCCESS(
                f"{mode}: countries +{summary.countries_created}/~{summary.countries_updated}; "
                f"currencies +{summary.currencies_created}/~{summary.currencies_updated}; "
                f"relationships +{summary.relationships_created}/~{summary.relationships_updated}"
            )
        )
