from datetime import date

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.countries.models import Country, CountryCurrency, Currency

SOURCE = "curated-demo-seed-v1"


class Command(BaseCommand):
    help = "Create a small deterministic country/currency slice for local development."

    @transaction.atomic
    def handle(self, *args, **options):
        countries = {
            "FI": ("FIN", "Finland"),
            "JP": ("JPN", "Japan"),
            "US": ("USA", "United States"),
        }
        currencies = {
            "EUR": ("Euro", "€", True),
            "JPY": ("Japanese yen", "¥", True),
            "USD": ("US dollar", "$", True),
            "FIM": ("Finnish markka", "mk", False),
        }

        country_rows = {}
        for iso2, (iso3, name) in countries.items():
            country_rows[iso2], _ = Country.objects.update_or_create(
                iso2=iso2,
                defaults={"iso3": iso3, "name": name, "official_name": name, "is_active": True},
            )

        currency_rows = {}
        for code, (name, symbol, active) in currencies.items():
            currency_rows[code], _ = Currency.objects.update_or_create(
                code=code,
                defaults={"name": name, "symbol": symbol, "is_active": active},
            )

        relationships = [
            ("FI", "FIM", True, None, date(2001, 12, 31), "historical_primary"),
            ("FI", "EUR", True, date(2002, 1, 1), None, "current_primary"),
            ("JP", "JPY", True, None, None, "current_primary"),
            ("US", "USD", True, None, None, "current_primary"),
        ]
        for iso2, code, primary, valid_from, valid_to, role in relationships:
            CountryCurrency.objects.update_or_create(
                country=country_rows[iso2],
                currency=currency_rows[code],
                valid_from=valid_from,
                valid_to=valid_to,
                defaults={"is_primary": primary, "usage_role": role, "source": SOURCE},
            )

        self.stdout.write(self.style.SUCCESS("Deterministic reference data is ready."))
