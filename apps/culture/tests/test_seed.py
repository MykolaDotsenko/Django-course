from __future__ import annotations

from io import StringIO

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from apps.culture.models import StoryMoment, StoryMomentStatus


@pytest.mark.django_db
def test_story_seed_requires_reference_data_first():
    with pytest.raises(CommandError, match="seed_reference_data"):
        call_command("seed_story_data")


@pytest.mark.django_db
def test_story_seed_is_reviewed_published_and_idempotent():
    call_command("seed_reference_data", stdout=StringIO())

    first = StringIO()
    call_command("seed_story_data", stdout=first)
    second = StringIO()
    call_command("seed_story_data", stdout=second)

    assert StoryMoment.objects.count() == 3
    assert StoryMoment.objects.filter(status=StoryMomentStatus.PUBLISHED).count() == 3
    assert "created=3, existing=0" in first.getvalue()
    assert "created=0, existing=3" in second.getvalue()

    euro_cash = StoryMoment.objects.get(external_id="curated:fi-euro-cash-changeover")
    assert euro_cash.source_name == "European Commission"
    assert euro_cash.countries.filter(iso2="FI").exists()
    assert euro_cash.currencies.filter(code="EUR").exists()
