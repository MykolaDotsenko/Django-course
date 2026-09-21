from __future__ import annotations

import re
from datetime import date, datetime
from urllib.parse import urlsplit

from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils import timezone

from apps.countries.models import CountryCurrency
from apps.culture.models import (
    StoryDatePrecision,
    StoryMoment,
    StoryMomentCategory,
    StoryMomentStatus,
)

_CAUSAL_RE = re.compile(
    r"\b(?:because|caused|causes|led to|leads to|resulted in|due to|as a result)\b",
    re.IGNORECASE,
)
_TEMPORAL_CATEGORIES = frozenset(
    {
        StoryMomentCategory.CURRENCY_INTRODUCTION,
        StoryMomentCategory.CURRENCY_RETIREMENT,
        StoryMomentCategory.REDENOMINATION,
        StoryMomentCategory.MONETARY_UNION,
        StoryMomentCategory.CASH_CHANGEOVER,
    }
)


class StoryPublicationError(ValueError):
    pass


def _validate_https_url(value: str) -> None:
    parsed = urlsplit(value)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise StoryPublicationError(
            "Story source URL must be an absolute credential-free HTTPS URL."
        )


def _validate_publishable(moment: StoryMoment) -> None:
    if not moment.title.strip() or not moment.summary.strip():
        raise StoryPublicationError("Story moments require title and summary.")
    if not moment.source_name.strip() or not moment.source_url.strip():
        raise StoryPublicationError("Story moments require source name and URL.")
    _validate_https_url(moment.source_url)
    if moment.verified_at is None:
        raise StoryPublicationError("Story moments require explicit editorial verification.")
    if not moment.countries.exists() and not moment.currencies.exists():
        raise StoryPublicationError(
            "Story moments require at least one country or currency relationship."
        )
    if moment.category in _TEMPORAL_CATEGORIES:
        if moment.start_date is None:
            raise StoryPublicationError("Temporal story moments require start_date.")
        if moment.date_precision == StoryDatePrecision.UNKNOWN:
            raise StoryPublicationError("Temporal story moments require date precision.")
    if _CAUSAL_RE.search(moment.summary):
        if not moment.supports_causality or not moment.causal_support_note.strip():
            raise StoryPublicationError(
                "Causal story wording requires explicit source support and an editorial note."
            )
    try:
        moment.full_clean()
    except ValidationError as exc:
        raise StoryPublicationError(str(exc)) from exc


def approve_story_moment(
    moment: StoryMoment,
    *,
    reviewed_at: datetime | None = None,
) -> StoryMoment:
    if moment.status in {
        StoryMomentStatus.PUBLISHED,
        StoryMomentStatus.RETIRED,
        StoryMomentStatus.REJECTED,
    }:
        raise StoryPublicationError(f"Cannot approve story in {moment.status} state.")
    previous_reviewed_at = moment.reviewed_at
    moment.reviewed_at = reviewed_at or timezone.now()
    try:
        _validate_publishable(moment)
    except Exception:
        moment.reviewed_at = previous_reviewed_at
        raise
    moment.status = StoryMomentStatus.APPROVED
    moment.save(update_fields=("status", "reviewed_at", "updated_at"))
    return moment


def publish_story_moment(
    moment: StoryMoment,
    *,
    published_at: datetime | None = None,
) -> StoryMoment:
    if moment.status != StoryMomentStatus.APPROVED:
        raise StoryPublicationError("Only approved story moments can be published.")
    _validate_publishable(moment)
    moment.status = StoryMomentStatus.PUBLISHED
    moment.published_at = published_at or timezone.now()
    moment.save(update_fields=("status", "published_at", "updated_at"))
    return moment


def retire_story_moment(moment: StoryMoment) -> StoryMoment:
    if moment.status != StoryMomentStatus.PUBLISHED:
        raise StoryPublicationError("Only published story moments can be retired.")
    moment.status = StoryMomentStatus.RETIRED
    moment.save(update_fields=("status", "updated_at"))
    return moment


def reject_story_moment(moment: StoryMoment) -> StoryMoment:
    if moment.status in {StoryMomentStatus.PUBLISHED, StoryMomentStatus.RETIRED}:
        raise StoryPublicationError("Published or retired stories cannot be rejected in place.")
    moment.status = StoryMomentStatus.REJECTED
    moment.reviewed_at = timezone.now()
    moment.save(update_fields=("status", "reviewed_at", "updated_at"))
    return moment


def select_story_moments(
    *,
    country_codes: tuple[str, ...],
    currency_codes: tuple[str, ...],
    selected_date: date,
    historical: bool,
    limit: int = 4,
) -> tuple[StoryMoment, ...]:
    if not 1 <= limit <= 8:
        raise ValueError("Story moment selection limit must be between 1 and 8.")

    filters = Q()
    if country_codes:
        filters |= Q(countries__iso2__in=country_codes)
    if currency_codes:
        filters |= Q(currencies__code__in=currency_codes)
    if not filters:
        return ()

    queryset = (
        StoryMoment.objects.published()
        .relevant_on(selected_date, historical=historical)
        .filter(filters)
        .prefetch_related("countries", "currencies")
        .distinct()
    )
    return tuple(queryset[:limit])


def currency_era_links(
    *,
    country_codes: tuple[str, ...],
    currency_codes: tuple[str, ...],
    selected_date: date,
) -> tuple[CountryCurrency, ...]:
    if not country_codes or not currency_codes:
        return ()
    return tuple(
        CountryCurrency.objects.on_date(selected_date)
        .filter(
            country__iso2__in=country_codes,
            currency__code__in=currency_codes,
        )
        .select_related("country", "currency")
        .order_by("country__name", "-is_primary", "-valid_from")
    )
