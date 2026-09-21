from __future__ import annotations

from datetime import date

from django.utils import timezone

from apps.countries.models import Country, Currency
from apps.culture.models import (
    StoryDatePrecision,
    StoryMoment,
    StoryMomentCategory,
    StoryMomentStatus,
    StorySourceKind,
)
from apps.culture.services import approve_story_moment, publish_story_moment

_FINLAND_EURO_SOURCE = (
    "https://economy-finance.ec.europa.eu/euro/eu-countries-and-euro/finland-and-euro_en"
)
_JAPAN_YEN_SOURCE = "https://www.boj.or.jp/en/about/education/oshiete/money/c02.htm"


def seed_demo_story_moments() -> tuple[int, int]:
    finland = Country.objects.get(iso2="FI")
    japan = Country.objects.get(iso2="JP")
    eur = Currency.objects.get(code="EUR")
    fim = Currency.objects.get(code="FIM")
    jpy = Currency.objects.get(code="JPY")

    specifications = (
        {
            "external_id": "curated:fi-euro-adoption",
            "category": StoryMomentCategory.MONETARY_UNION,
            "title": "Finland adopted the euro",
            "summary": (
                "Finland adopted the euro on 1 January 1999. During the following three-year "
                "transition, the euro was the official currency but existed only as book money."
            ),
            "start_date": date(1999, 1, 1),
            "end_date": date(1999, 1, 1),
            "date_precision": StoryDatePrecision.EXACT_DAY,
            "source_name": "European Commission",
            "source_url": _FINLAND_EURO_SOURCE,
            "relevance_weight": 96,
            "countries": (finland,),
            "currencies": (eur, fim),
        },
        {
            "external_id": "curated:fi-euro-cash-changeover",
            "category": StoryMomentCategory.CASH_CHANGEOVER,
            "title": "Euro cash arrived in Finland",
            "summary": (
                "Euro banknotes and coins entered circulation in Finland on 1 January 2002. "
                "The dual-circulation period with the Finnish markka ended on 28 February 2002."
            ),
            "start_date": date(2002, 1, 1),
            "end_date": date(2002, 2, 28),
            "date_precision": StoryDatePrecision.RANGE,
            "source_name": "European Commission",
            "source_url": _FINLAND_EURO_SOURCE,
            "relevance_weight": 100,
            "countries": (finland,),
            "currencies": (eur, fim),
        },
        {
            "external_id": "curated:jp-yen-introduction",
            "category": StoryMomentCategory.CURRENCY_INTRODUCTION,
            "title": "The yen became Japan's currency unit",
            "summary": (
                "Japan's government enacted the New Currency Act in 1871 and introduced the yen "
                "as the new currency unit."
            ),
            "start_date": date(1871, 1, 1),
            "end_date": date(1871, 12, 31),
            "date_precision": StoryDatePrecision.YEAR,
            "source_name": "Bank of Japan",
            "source_url": _JAPAN_YEN_SOURCE,
            "relevance_weight": 92,
            "countries": (japan,),
            "currencies": (jpy,),
        },
    )

    created = existing = 0
    for spec in specifications:
        moment = StoryMoment.objects.filter(
            source_kind=StorySourceKind.OFFICIAL,
            external_id=spec["external_id"],
        ).first()
        if moment is not None:
            existing += 1
            continue

        moment = StoryMoment.objects.create(
            source_kind=StorySourceKind.OFFICIAL,
            external_id=spec["external_id"],
            category=spec["category"],
            title=spec["title"],
            summary=spec["summary"],
            start_date=spec["start_date"],
            end_date=spec["end_date"],
            date_precision=spec["date_precision"],
            source_name=spec["source_name"],
            source_url=spec["source_url"],
            relevance_weight=spec["relevance_weight"],
            verified_at=timezone.now(),
            status=StoryMomentStatus.NEEDS_REVIEW,
        )
        moment.countries.set(spec["countries"])
        moment.currencies.set(spec["currencies"])
        approve_story_moment(moment)
        publish_story_moment(moment)
        created += 1

    return created, existing
