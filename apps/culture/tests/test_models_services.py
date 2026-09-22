from __future__ import annotations

from datetime import date

import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.countries.models import Country, CountryCurrency, Currency
from apps.culture.models import (
    StoryDatePrecision,
    StoryMoment,
    StoryMomentCategory,
    StoryMomentStatus,
    StorySourceKind,
)
from apps.culture.services import (
    StoryPublicationError,
    approve_story_moment,
    publish_story_moment,
    reject_story_moment,
    retire_story_moment,
    select_story_moments,
)


@pytest.fixture
def finland(db):
    return Country.objects.create(iso2="FI", iso3="FIN", name="Finland")


@pytest.fixture
def euro(db):
    return Currency.objects.create(code="EUR", name="Euro", symbol="€")


def _moment(*, title="Euro context", summary="A sourced monetary-history fact."):
    return StoryMoment.objects.create(
        category=StoryMomentCategory.MONETARY_UNION,
        title=title,
        summary=summary,
        start_date=date(1999, 1, 1),
        end_date=date(1999, 1, 1),
        date_precision=StoryDatePrecision.EXACT_DAY,
        source_kind=StorySourceKind.OFFICIAL,
        source_name="Official source",
        source_url="https://example.org/story",
        verified_at=timezone.now(),
        status=StoryMomentStatus.NEEDS_REVIEW,
        relevance_weight=90,
    )


@pytest.mark.django_db
def test_story_model_rejects_reversed_date_range():
    moment = StoryMoment(
        category=StoryMomentCategory.CASH_CHANGEOVER,
        title="Bad range",
        summary="Bad range.",
        start_date=date(2002, 2, 28),
        end_date=date(2002, 1, 1),
        date_precision=StoryDatePrecision.RANGE,
        source_kind=StorySourceKind.OFFICIAL,
        source_name="Source",
        source_url="https://example.org",
    )

    with pytest.raises(ValidationError, match="end_date"):
        moment.full_clean()


@pytest.mark.django_db
def test_dated_story_requires_explicit_temporal_precision():
    moment = StoryMoment(
        category=StoryMomentCategory.CURRENCY_INTRODUCTION,
        title="Introduction",
        summary="A sourced introduction.",
        start_date=date(1871, 1, 1),
        source_kind=StorySourceKind.OFFICIAL,
        source_name="Source",
        source_url="https://example.org",
    )

    with pytest.raises(ValidationError, match="temporal precision"):
        moment.full_clean()


@pytest.mark.django_db
def test_story_requires_relation_and_provenance_before_approval(finland):
    moment = _moment()
    moment.verified_at = None
    moment.save(update_fields=("verified_at",))

    with pytest.raises(StoryPublicationError, match="verification"):
        approve_story_moment(moment)

    moment.verified_at = timezone.now()
    moment.save(update_fields=("verified_at",))
    with pytest.raises(StoryPublicationError, match="country or currency"):
        approve_story_moment(moment)

    moment.countries.add(finland)
    approve_story_moment(moment)
    assert moment.status == StoryMomentStatus.APPROVED

    publish_story_moment(moment)
    assert moment.status == StoryMomentStatus.PUBLISHED
    assert moment.published_at is not None


@pytest.mark.django_db
def test_causal_wording_requires_explicit_source_support(finland):
    moment = _moment(
        summary="The policy caused the exchange rate to move.",
    )
    moment.countries.add(finland)

    with pytest.raises(StoryPublicationError, match="Causal"):
        approve_story_moment(moment)

    moment.supports_causality = True
    moment.causal_support_note = "The reviewed source explicitly makes this causal claim."
    moment.save(update_fields=("supports_causality", "causal_support_note"))
    approve_story_moment(moment)

    assert moment.status == StoryMomentStatus.APPROVED


@pytest.mark.django_db
def test_story_approval_rejects_credentialed_https_provenance(finland):
    moment = _moment()
    moment.source_url = "https://user:secret@example.org/story"
    moment.save(update_fields=("source_url",))
    moment.countries.add(finland)

    with pytest.raises(StoryPublicationError, match="credential-free HTTPS"):
        approve_story_moment(moment)


@pytest.mark.django_db
def test_publish_requires_approved_state(finland):
    moment = _moment()
    moment.countries.add(finland)

    with pytest.raises(StoryPublicationError, match="approved"):
        publish_story_moment(moment)


@pytest.mark.django_db
def test_published_story_can_be_retired_but_not_rejected(finland):
    moment = _moment()
    moment.countries.add(finland)
    approve_story_moment(moment)
    publish_story_moment(moment)
    retire_story_moment(moment)

    assert moment.status == StoryMomentStatus.RETIRED
    with pytest.raises(StoryPublicationError, match="cannot be rejected"):
        reject_story_moment(moment)


@pytest.mark.django_db
def test_reject_marks_unpublished_candidate_reviewed(finland):
    moment = _moment()
    moment.countries.add(finland)

    reject_story_moment(moment)

    assert moment.status == StoryMomentStatus.REJECTED
    assert moment.reviewed_at is not None


@pytest.mark.django_db
def test_historical_selection_excludes_unpublished_and_out_of_range(finland, euro):
    in_range = _moment(title="In range")
    in_range.start_date = date(2002, 1, 1)
    in_range.end_date = date(2002, 2, 28)
    in_range.date_precision = StoryDatePrecision.RANGE
    in_range.save()
    in_range.countries.add(finland)
    in_range.currencies.add(euro)
    approve_story_moment(in_range)
    publish_story_moment(in_range)

    unpublished = _moment(title="Unpublished")
    unpublished.start_date = date(2002, 1, 1)
    unpublished.end_date = date(2002, 2, 28)
    unpublished.date_precision = StoryDatePrecision.RANGE
    unpublished.save()
    unpublished.countries.add(finland)

    future = _moment(title="Future")
    future.start_date = date(2003, 1, 1)
    future.end_date = date(2003, 1, 1)
    future.save()
    future.countries.add(finland)
    approve_story_moment(future)
    publish_story_moment(future)

    selected = select_story_moments(
        country_codes=("FI",),
        currency_codes=("EUR",),
        selected_date=date(2002, 1, 15),
        historical=True,
    )

    assert [moment.title for moment in selected] == ["In range"]


@pytest.mark.django_db
def test_current_story_can_include_reviewed_past_money_history(finland):
    moment = _moment(title="Past transition")
    moment.countries.add(finland)
    approve_story_moment(moment)
    publish_story_moment(moment)

    selected = select_story_moments(
        country_codes=("FI",),
        currency_codes=(),
        selected_date=date(2026, 9, 21),
        historical=False,
    )

    assert selected == (moment,)


@pytest.mark.django_db
def test_story_selection_limit_is_bounded():
    with pytest.raises(ValueError, match="between 1 and 8"):
        select_story_moments(
            country_codes=("FI",),
            currency_codes=(),
            selected_date=date(2026, 9, 21),
            historical=False,
            limit=9,
        )


@pytest.mark.django_db
def test_currency_relationship_can_carry_canonical_source(finland, euro):
    link = CountryCurrency.objects.create(
        country=finland,
        currency=euro,
        is_primary=True,
        valid_from=date(2002, 1, 1),
        usage_role="current_primary",
        source="https://example.org/currency",
    )

    assert link.source.startswith("https://")


@pytest.mark.django_db
def test_published_story_editorial_content_is_immutable(finland):
    moment = _moment(title="Published fact")
    moment.countries.add(finland)
    approve_story_moment(moment)
    publish_story_moment(moment)

    moment.summary = "Quietly edited after publication."
    with pytest.raises(ValidationError, match="immutable"):
        moment.save()


@pytest.mark.django_db
def test_published_story_relations_are_immutable(finland, euro):
    moment = _moment(title="Published relations")
    moment.countries.add(finland)
    approve_story_moment(moment)
    publish_story_moment(moment)

    with pytest.raises(ValidationError, match="relationships are immutable"):
        moment.currencies.add(euro)

    with pytest.raises(ValidationError, match="relationships are immutable"):
        moment.countries.clear()


@pytest.mark.django_db
def test_retired_story_cannot_be_resurrected(finland):
    moment = _moment(title="Retired fact")
    moment.countries.add(finland)
    approve_story_moment(moment)
    publish_story_moment(moment)
    retire_story_moment(moment)

    moment.status = StoryMomentStatus.PUBLISHED
    with pytest.raises(ValidationError, match="Retired stories are immutable"):
        moment.save()


@pytest.mark.django_db
def test_story_summary_has_bounded_editorial_length(finland):
    moment = _moment(summary="x" * 2001)
    moment.countries.add(finland)

    with pytest.raises(StoryPublicationError, match="2000"):
        approve_story_moment(moment)
