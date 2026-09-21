from __future__ import annotations

from io import StringIO

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from apps.media.models import MediaKind, MediaRole, MediaSourceKind, MediaStatus
from apps.media.sources.base import MediaCandidate


@pytest.mark.django_db
def test_wikimedia_ingestion_command_creates_review_candidate_only(monkeypatch):
    monkeypatch.setattr(
        "apps.media.management.commands.ingest_media_candidates.WikimediaCommonsClient.search",
        lambda self, query, limit: (
            MediaCandidate(
                source_kind=MediaSourceKind.WIKIMEDIA_COMMONS,
                external_id="123",
                title="Helsinki",
                source_name="Wikimedia Commons",
                source_url="https://commons.wikimedia.org/wiki/File:Helsinki.jpg",
                source_media_url="https://upload.wikimedia.org/helsinki.jpg",
                creator="Creator",
                licence_id="CC BY 4.0",
                rights_statement="CC BY 4.0",
                attribution_text="Creator · CC BY 4.0",
            ),
        ),
    )
    stdout = StringIO()

    call_command(
        "ingest_media_candidates",
        source="wikimedia",
        query="Helsinki historical money",
        role=MediaRole.HISTORICAL_TIMELINE,
        kind=MediaKind.ARCHIVAL_PHOTO,
        limit=1,
        stdout=stdout,
    )

    from apps.media.models import MediaAsset

    asset = MediaAsset.objects.get()
    assert asset.status == MediaStatus.NEEDS_REVIEW
    assert not asset.storage_file
    assert asset.published_at is None
    assert "APPLIED: +1" in stdout.getvalue()


@pytest.mark.django_db
def test_europeana_command_requires_server_side_api_key(monkeypatch):
    monkeypatch.delenv("EUROPEANA_API_KEY", raising=False)

    with pytest.raises(CommandError, match="EUROPEANA_API_KEY"):
        call_command(
            "ingest_media_candidates",
            source="europeana",
            query="markka",
            role=MediaRole.HISTORICAL_TIMELINE,
            kind=MediaKind.ARCHIVAL_PHOTO,
        )


@pytest.mark.django_db
def test_ingestion_command_rejects_unknown_country_before_network(monkeypatch):
    called = False

    def unexpected_search(self, query, limit):
        nonlocal called
        called = True
        return ()

    monkeypatch.setattr(
        "apps.media.management.commands.ingest_media_candidates.WikimediaCommonsClient.search",
        unexpected_search,
    )

    with pytest.raises(CommandError, match="Unknown country"):
        call_command(
            "ingest_media_candidates",
            source="wikimedia",
            query="test",
            role=MediaRole.COUNTRY_HERO,
            kind=MediaKind.CONTEMPORARY_PHOTO,
            country="ZZ",
        )

    assert called is False
