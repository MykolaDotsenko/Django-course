from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.countries.models import Country, Currency
from apps.culture.seed import seed_demo_destination_context


class Command(BaseCommand):
    help = "Create the small sourced destination-context slice used by the portfolio demo."

    @transaction.atomic
    def handle(self, *args, **options):
        if not Country.objects.filter(iso2="JP").exists() or not Currency.objects.filter(
            code="JPY"
        ).exists():
            raise CommandError(
                "Japan/JPY reference data is missing. Run seed_reference_data first."
            )

        created, existing = seed_demo_destination_context()
        self.stdout.write(
            self.style.SUCCESS(
                f"Destination context is ready: created={created}, existing={existing}."
            )
        )
