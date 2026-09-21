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
            "EUR": ("Euro", "€", True, None, None),
            "JPY": ("Japanese yen", "¥", True, None, None),
            "USD": ("US dollar", "$", True, None, None),
            "FIM": ("Finnish markka", "mk", False, None, date(2001, 12, 31)),
        }

        country_rows = {}
        for iso2, (iso3, name) in countries.items():
            country_rows[iso2], _ = Country.objects.update_or_create(
                iso2=iso2,
                defaults={"iso3": iso3, "name": name, "official_name": name, "is_active": True},
            )

        currency_rows = {}
        for code, (name, symbol, active, active_from, active_to) in currencies.items():
            currency_rows[code], _ = Currency.objects.update_or_create(
                code=code,
                defaults={
                    "name": name,
                    "symbol": symbol,
                    "is_active": active,
                    "active_from": active_from,
                    "active_to": active_to,
                },
            )

        relationships = [
            (
                "FI",
                "FIM",
                True,
                None,
                date(2001, 12, 31),
                "historical_primary",
                "https://economy-finance.ec.europa.eu/euro/eu-countries-and-euro/finland-and-euro_en",
            ),
            (
                "FI",
                "EUR",
                True,
                date(2002, 1, 1),
                None,
                "current_primary",
                "https://economy-finance.ec.europa.eu/euro/eu-countries-and-euro/finland-and-euro_en",
            ),
            (
                "JP",
                "JPY",
                True,
                None,
                None,
                "current_primary",
                "https://www.boj.or.jp/en/about/education/oshiete/money/c02.htm",
            ),
            ("US", "USD", True, None, None, "current_primary", SOURCE),
        ]
        for iso2, code, primary, valid_from, valid_to, role, source in relationships:
            CountryCurrency.objects.update_or_create(
                country=country_rows[iso2],
                currency=currency_rows[code],
                valid_from=valid_from,
                valid_to=valid_to,
                defaults={"is_primary": primary, "usage_role": role, "source": source},
            )

        self.stdout.write(self.style.SUCCESS("Deterministic reference data is ready."))
