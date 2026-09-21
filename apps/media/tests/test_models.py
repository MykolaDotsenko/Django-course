from __future__ import annotations

from datetime import date

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from apps.media.models import (
    DatePrecision,
    MediaAsset,
    MediaKind,
    MediaRole,
    MediaSourceKind,
)


@pytest.mark.django_db
def test_media_asset_rejects_generated_source_without_ai_flag():
    asset = MediaAsset(
        kind=MediaKind.GENERATED_ILLUSTRATION,
        source_kind=MediaSourceKind.GENERATED,
        role=MediaRole.STORY_COVER,
        title="Generated candidate",
        generated_by_ai=False,
    )

    with pytest.raises(ValidationError, match="generated_by_ai"):
        asset.full_clean()


@pytest.mark.django_db
def test_media_asset_rejects_reversed_temporal_scope():
    asset = MediaAsset(
        kind=MediaKind.ARCHIVAL_PHOTO,
        source_kind=MediaSourceKind.WIKIMEDIA_COMMONS,
        role=MediaRole.HISTORICAL_TIMELINE,
        title="Archive",
        valid_from=date(2000, 1, 1),
        valid_to=date(1999, 1, 1),
        date_precision=DatePrecision.RANGE,
    )

    with pytest.raises(ValidationError, match="valid_to"):
        asset.full_clean()


@pytest.mark.django_db
def test_external_identity_is_unique_per_source():
    MediaAsset.objects.create(
        kind=MediaKind.ARTWORK,
        source_kind=MediaSourceKind.WIKIMEDIA_COMMONS,
        role=MediaRole.STORY_COVER,
        title="One",
        external_id="42",
    )

    with pytest.raises(IntegrityError), transaction.atomic():
        MediaAsset.objects.create(
            kind=MediaKind.ARTWORK,
            source_kind=MediaSourceKind.WIKIMEDIA_COMMONS,
            role=MediaRole.STORY_COVER,
            title="Two",
            external_id="42",
        )


@pytest.mark.django_db
def test_same_external_id_is_allowed_for_different_sources():
    MediaAsset.objects.create(
        kind=MediaKind.ARTWORK,
        source_kind=MediaSourceKind.WIKIMEDIA_COMMONS,
        role=MediaRole.STORY_COVER,
        title="Commons",
        external_id="42",
    )
    MediaAsset.objects.create(
        kind=MediaKind.ARTWORK,
        source_kind=MediaSourceKind.EUROPEANA,
        role=MediaRole.STORY_COVER,
        title="Europeana",
        external_id="42",
    )

    assert MediaAsset.objects.count() == 2
