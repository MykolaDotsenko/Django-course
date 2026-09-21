from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.countries.models import Country, Currency
from apps.culture.seed import seed_demo_story_moments


class Command(BaseCommand):
    help = "Create the small deterministic reviewed story slice used by the portfolio demo."

    @transaction.atomic
    def handle(self, *args, **options):
        required_countries = {"FI", "JP"}
        required_currencies = {"EUR", "FIM", "JPY"}
        if (
            set(Country.objects.filter(iso2__in=required_countries).values_list("iso2", flat=True))
            != required_countries
            or set(
                Currency.objects.filter(code__in=required_currencies).values_list(
                    "code", flat=True
                )
            )
            != required_currencies
        ):
            raise CommandError(
                "Reference country/currency data is missing. Run seed_reference_data first."
            )

        created, existing = seed_demo_story_moments()
        self.stdout.write(
            self.style.SUCCESS(
                f"Deterministic story data is ready: created={created}, existing={existing}."
            )
        )
