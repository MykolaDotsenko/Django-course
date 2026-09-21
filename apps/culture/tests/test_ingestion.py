from __future__ import annotations

from datetime import UTC, date, datetime
from io import StringIO

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError
from django.utils import timezone

from apps.countries.models import Country, Currency
from apps.culture.ingestion import upsert_wikidata_story_candidate
from apps.culture.models import (
    StoryDatePrecision,
    StoryMoment,
    StoryMomentCategory,
    StoryMomentStatus,
)
from apps.culture.services import approve_story_moment, publish_story_moment
from integrations.wikidata import WikidataItem


@pytest.fixture
def finland(db):
    return Country.objects.create(iso2="FI", iso3="FIN", name="Finland")


@pytest.fixture
def euro(db):
    return Currency.objects.create(code="EUR", name="Euro", symbol="€")


@pytest.fixture
def item():
    return WikidataItem(
        item_id="Q4916",
        label="euro",
        description="currency of the eurozone",
        source_url="https://www.wikidata.org/wiki/Q4916",
        retrieved_at=datetime(2026, 9, 21, tzinfo=UTC),
    )


@pytest.mark.django_db
def test_wikidata_ingestion_creates_unpublished_review_candidate(item, finland, euro):
    result = upsert_wikidata_story_candidate(
        item,
        category=StoryMomentCategory.MONETARY_UNION,
        country=finland,
        currency=euro,
        start_date=date(1999, 1, 1),
        end_date=date(1999, 1, 1),
        date_precision=StoryDatePrecision.EXACT_DAY,
        relevance_weight=90,
    )

    assert result.created is True
    moment = StoryMoment.objects.get()
    assert moment.status == StoryMomentStatus.NEEDS_REVIEW
    assert moment.verified_at is None
    assert list(moment.countries.all()) == [finland]
    assert list(moment.currencies.all()) == [euro]


@pytest.mark.django_db
def test_wikidata_ingestion_is_idempotent_and_dry_run_rolls_back(item, finland):
    dry = upsert_wikidata_story_candidate(
        item,
        category=StoryMomentCategory.CULTURAL_MONEY_FACT,
        country=finland,
        currency=None,
        start_date=None,
        end_date=None,
        date_precision=StoryDatePrecision.UNKNOWN,
        relevance_weight=50,
        dry_run=True,
    )
    assert dry.created is True
    assert not StoryMoment.objects.exists()

    first = upsert_wikidata_story_candidate(
        item,
        category=StoryMomentCategory.CULTURAL_MONEY_FACT,
        country=finland,
        currency=None,
        start_date=None,
        end_date=None,
        date_precision=StoryDatePrecision.UNKNOWN,
        relevance_weight=50,
    )
    second = upsert_wikidata_story_candidate(
        item,
        category=StoryMomentCategory.CULTURAL_MONEY_FACT,
        country=finland,
        currency=None,
        start_date=None,
        end_date=None,
        date_precision=StoryDatePrecision.UNKNOWN,
        relevance_weight=50,
    )

    assert first.created is True
    assert second.created is False
    assert second.updated is False
    assert StoryMoment.objects.count() == 1


@pytest.mark.django_db
def test_reviewed_story_is_protected_from_upstream_candidate_overwrite(item, finland):
    result = upsert_wikidata_story_candidate(
        item,
        category=StoryMomentCategory.CULTURAL_MONEY_FACT,
        country=finland,
        currency=None,
        start_date=None,
        end_date=None,
        date_precision=StoryDatePrecision.UNKNOWN,
        relevance_weight=50,
    )
    moment = StoryMoment.objects.get(pk=result.story_moment_id)
    moment.verified_at = timezone.now()
    moment.save(update_fields=("verified_at",))
    approve_story_moment(moment)
    publish_story_moment(moment)

    changed = WikidataItem(
        item_id=item.item_id,
        label="Changed upstream label",
        description="Changed description",
        source_url=item.source_url,
        retrieved_at=item.retrieved_at,
    )
    protected = upsert_wikidata_story_candidate(
        changed,
        category=StoryMomentCategory.CULTURAL_MONEY_FACT,
        country=finland,
        currency=None,
        start_date=None,
        end_date=None,
        date_precision=StoryDatePrecision.UNKNOWN,
        relevance_weight=10,
    )

    moment.refresh_from_db()
    assert protected.protected is True
    assert moment.title == "euro"
    assert moment.status == StoryMomentStatus.PUBLISHED


@pytest.mark.django_db
def test_ingestion_rejects_invalid_range(item, finland):
    with pytest.raises(ValueError, match="end_date"):
        upsert_wikidata_story_candidate(
            item,
            category=StoryMomentCategory.CASH_CHANGEOVER,
            country=finland,
            currency=None,
            start_date=date(2002, 2, 28),
            end_date=date(2002, 1, 1),
            date_precision=StoryDatePrecision.RANGE,
            relevance_weight=50,
        )


@pytest.mark.django_db
def test_management_command_never_publishes_candidate(monkeypatch, finland):
    monkeypatch.setattr(
        "apps.culture.management.commands.ingest_story_candidate.WikidataItemClient.get_item",
        lambda self, item_id: WikidataItem(
            item_id="Q4916",
            label="euro",
            description="currency of the eurozone",
            source_url="https://www.wikidata.org/wiki/Q4916",
            retrieved_at=datetime(2026, 9, 21, tzinfo=UTC),
        ),
    )
    stdout = StringIO()
    call_command(
        "ingest_story_candidate",
        item="Q4916",
        category=StoryMomentCategory.CULTURAL_MONEY_FACT,
        country="FI",
        date_precision=StoryDatePrecision.UNKNOWN,
        stdout=stdout,
    )

    moment = StoryMoment.objects.get()
    assert moment.status == StoryMomentStatus.NEEDS_REVIEW
    assert moment.published_at is None
    assert "created StoryMoment candidate" in stdout.getvalue()


@pytest.mark.django_db
def test_management_command_validates_relationship_before_network(monkeypatch):
    called = False

    def unexpected_get(self, item_id):
        nonlocal called
        called = True
        raise AssertionError

    monkeypatch.setattr(
        "apps.culture.management.commands.ingest_story_candidate.WikidataItemClient.get_item",
        unexpected_get,
    )

    with pytest.raises(CommandError, match="At least one"):
        call_command(
            "ingest_story_candidate",
            item="Q4916",
            category=StoryMomentCategory.CULTURAL_MONEY_FACT,
        )
    assert called is False


@pytest.mark.django_db
def test_wikidata_candidate_rejects_oversized_summary(item, finland):
    with pytest.raises(ValueError, match="2000"):
        upsert_wikidata_story_candidate(
            item,
            category=StoryMomentCategory.CULTURAL_MONEY_FACT,
            country=finland,
            currency=None,
            start_date=None,
            end_date=None,
            date_precision=StoryDatePrecision.UNKNOWN,
            relevance_weight=50,
            summary="x" * 2001,
        )
