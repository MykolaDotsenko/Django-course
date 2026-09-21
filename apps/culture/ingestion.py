from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from django.db import transaction

from apps.countries.models import Country, Currency
from apps.culture.models import (
    StoryDatePrecision,
    StoryMoment,
    StoryMomentCategory,
    StoryMomentStatus,
    StorySourceKind,
)
from integrations.wikidata import WikidataItem


@dataclass(frozen=True, slots=True)
class StoryCandidateIngestResult:
    created: bool
    updated: bool
    protected: bool
    dry_run: bool
    story_moment_id: int | None


def upsert_wikidata_story_candidate(
    item: WikidataItem,
    *,
    category: str,
    country: Country | None,
    currency: Currency | None,
    start_date: date | None,
    end_date: date | None,
    date_precision: str,
    relevance_weight: int,
    title: str | None = None,
    summary: str | None = None,
    dry_run: bool = False,
) -> StoryCandidateIngestResult:
    if category not in StoryMomentCategory.values:
        raise ValueError("Unknown story category.")
    if date_precision not in StoryDatePrecision.values:
        raise ValueError("Unknown story date precision.")
    if not 0 <= relevance_weight <= 100:
        raise ValueError("Story relevance weight must be between 0 and 100.")
    if start_date and end_date and end_date < start_date:
        raise ValueError("Story end_date cannot precede start_date.")

    protected_statuses = {
        StoryMomentStatus.APPROVED,
        StoryMomentStatus.PUBLISHED,
        StoryMomentStatus.RETIRED,
    }

    with transaction.atomic():
        existing = StoryMoment.objects.filter(
            source_kind=StorySourceKind.WIKIDATA,
            external_id=item.item_id,
        ).first()
        if existing is not None and existing.status in protected_statuses:
            return StoryCandidateIngestResult(
                created=False,
                updated=False,
                protected=True,
                dry_run=dry_run,
                story_moment_id=existing.pk,
            )

        defaults = {
            "category": category,
            "title": (title or item.label).strip()[:240],
            "summary": (summary or item.description).strip(),
            "start_date": start_date,
            "end_date": end_date,
            "date_precision": date_precision,
            "source_name": "Wikidata",
            "source_url": item.source_url,
            "source_retrieved_at": item.retrieved_at,
            "relevance_weight": relevance_weight,
            "supports_causality": False,
            "causal_support_note": "",
            "status": StoryMomentStatus.NEEDS_REVIEW,
            "verified_at": None,
            "reviewed_at": None,
            "published_at": None,
        }

        if existing is None:
            moment = StoryMoment.objects.create(
                source_kind=StorySourceKind.WIKIDATA,
                external_id=item.item_id,
                **defaults,
            )
            created = True
            updated = False
        else:
            dirty_fields: list[str] = []
            for field_name, value in defaults.items():
                if getattr(existing, field_name) != value:
                    setattr(existing, field_name, value)
                    dirty_fields.append(field_name)
            if dirty_fields:
                existing.save(update_fields=(*dirty_fields, "updated_at"))
            moment = existing
            created = False
            updated = bool(dirty_fields)

        if country is not None:
            moment.countries.set([country])
        else:
            moment.countries.clear()
        if currency is not None:
            moment.currencies.set([currency])
        else:
            moment.currencies.clear()

        if dry_run:
            transaction.set_rollback(True)
            moment_id = None
        else:
            moment_id = moment.pk

    return StoryCandidateIngestResult(
        created=created,
        updated=updated,
        protected=False,
        dry_run=dry_run,
        story_moment_id=moment_id,
    )
