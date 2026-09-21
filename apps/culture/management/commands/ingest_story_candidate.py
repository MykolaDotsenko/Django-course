from __future__ import annotations

from datetime import date

from django.core.management.base import BaseCommand, CommandError

from apps.countries.models import Country, Currency
from apps.culture.ingestion import upsert_wikidata_story_candidate
from apps.culture.models import StoryDatePrecision, StoryMomentCategory
from integrations.wikidata import WikidataItemClient, WikidataSourceError


class Command(BaseCommand):
    help = (
        "Fetch one explicit Wikidata item and create/update an unpublished StoryMoment "
        "candidate. This command never publishes a story and is never used in web requests."
    )

    def add_arguments(self, parser):
        parser.add_argument("--item", required=True)
        parser.add_argument("--category", choices=StoryMomentCategory.values, required=True)
        parser.add_argument("--country")
        parser.add_argument("--currency")
        parser.add_argument("--start-date")
        parser.add_argument("--end-date")
        parser.add_argument(
            "--date-precision",
            choices=StoryDatePrecision.values,
            default=StoryDatePrecision.UNKNOWN,
        )
        parser.add_argument("--relevance-weight", type=int, default=50)
        parser.add_argument("--title")
        parser.add_argument("--summary")
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):
        country = self._country(options["country"])
        currency = self._currency(options["currency"])
        start_date = self._date(options["start_date"], "start-date")
        end_date = self._date(options["end_date"], "end-date")

        if country is None and currency is None:
            raise CommandError("At least one --country or --currency relation is required.")

        try:
            item = WikidataItemClient().get_item(options["item"])
            result = upsert_wikidata_story_candidate(
                item,
                category=options["category"],
                country=country,
                currency=currency,
                start_date=start_date,
                end_date=end_date,
                date_precision=options["date_precision"],
                relevance_weight=options["relevance_weight"],
                title=options["title"],
                summary=options["summary"],
                dry_run=options["dry_run"],
            )
        except (ValueError, WikidataSourceError) as exc:
            raise CommandError(str(exc)) from exc

        if result.protected:
            self.stdout.write(
                self.style.WARNING(
                    f"PROTECTED: existing reviewed story {result.story_moment_id} was not changed."
                )
            )
            return

        mode = "DRY RUN" if result.dry_run else "APPLIED"
        action = "created" if result.created else ("updated" if result.updated else "unchanged")
        self.stdout.write(self.style.SUCCESS(f"{mode}: {action} StoryMoment candidate."))

    @staticmethod
    def _country(value: str | None) -> Country | None:
        if not value:
            return None
        country = Country.objects.filter(iso2=value.upper()).first()
        if country is None:
            raise CommandError("Unknown country code.")
        return country

    @staticmethod
    def _currency(value: str | None) -> Currency | None:
        if not value:
            return None
        currency = Currency.objects.filter(code=value.upper()).first()
        if currency is None:
            raise CommandError("Unknown currency code.")
        return currency

    @staticmethod
    def _date(value: str | None, label: str) -> date | None:
        if not value:
            return None
        try:
            return date.fromisoformat(value)
        except ValueError as exc:
            raise CommandError(f"--{label} must be YYYY-MM-DD.") from exc
