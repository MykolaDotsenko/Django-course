from __future__ import annotations

import io
from io import StringIO

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import override_settings
from PIL import Image

from apps.countries.models import Country
from apps.media.catalog import FINLAND_COUNTRY_HERO
from apps.media.models import MediaAsset, MediaStatus
from apps.media.sources.base import DownloadedMedia


def _jpeg_bytes() -> bytes:
    output = io.BytesIO()
    Image.new("RGB", (32, 24), (90, 110, 120)).save(output, format="JPEG")
    return output.getvalue()


@pytest.fixture
def finland(db) -> Country:
    return Country.objects.create(iso2="FI", iso3="FIN", name="Finland")


@pytest.mark.django_db
def test_finland_media_bootstrap_requires_reference_country_before_network(monkeypatch):
    called = False

    def unexpected_download(self, media_url, max_bytes):
        nonlocal called
        called = True
        raise AssertionError("network should not be called")

    monkeypatch.setattr(
        "apps.media.management.commands.seed_finland_editorial_media."
        "WikimediaCommonsClient.download_media",
        unexpected_download,
    )

    with pytest.raises(CommandError, match="seed_reference_data"):
        call_command("seed_finland_editorial_media", download=True)

    assert called is False


@pytest.mark.django_db
def test_finland_media_bootstrap_dry_run_is_side_effect_free(finland, monkeypatch):
    called = False

    def unexpected_download(self, media_url, max_bytes):
        nonlocal called
        called = True
        raise AssertionError("network should not be called")

    monkeypatch.setattr(
        "apps.media.management.commands.seed_finland_editorial_media."
        "WikimediaCommonsClient.download_media",
        unexpected_download,
    )
    stdout = StringIO()

    call_command(
        "seed_finland_editorial_media",
        dry_run=True,
        download=True,
        stdout=stdout,
    )

    assert MediaAsset.objects.count() == 0
    assert called is False
    assert "DRY RUN" in stdout.getvalue()


@pytest.mark.django_db
def test_finland_media_bootstrap_creates_review_gated_canonical_metadata(finland):
    stdout = StringIO()

    call_command("seed_finland_editorial_media", stdout=stdout)

    asset = MediaAsset.objects.get()
    spec = FINLAND_COUNTRY_HERO
    assert asset.country == finland
    assert asset.role == spec.role
    assert asset.kind == spec.kind
    assert asset.city == "Helsinki"
    assert asset.alt_text == spec.alt_text
    assert asset.source_url == spec.source_url
    assert asset.source_media_url == spec.source_media_url
    assert asset.creator == "JIP"
    assert asset.licence_id == "CC BY-SA 4.0"
    assert asset.attribution_text == "JIP · Wikimedia Commons · CC BY-SA 4.0"
    assert asset.generated_by_ai is False
    assert asset.status == MediaStatus.NEEDS_REVIEW
    assert not asset.storage_file
    assert asset.reviewed_at is None
    assert asset.published_at is None
    assert "metadata-only" in stdout.getvalue()


@pytest.mark.django_db
def test_finland_media_bootstrap_downloads_sanitizes_and_remains_review_gated(
    finland,
    monkeypatch,
    tmp_path,
):
    payload = _jpeg_bytes()
    seen = {}

    def fake_download(self, media_url, max_bytes=10 * 1024 * 1024):
        seen["url"] = media_url
        return DownloadedMedia(
            data=payload,
            filename="Helsinki_tram.jpg",
            mime_type="image/jpeg",
        )

    monkeypatch.setattr(
        "apps.media.management.commands.seed_finland_editorial_media."
        "WikimediaCommonsClient.download_media",
        fake_download,
    )
    stdout = StringIO()

    with override_settings(MEDIA_ROOT=tmp_path):
        call_command(
            "seed_finland_editorial_media",
            download=True,
            stdout=stdout,
        )
        asset = MediaAsset.objects.get()

        assert seen["url"] == FINLAND_COUNTRY_HERO.source_media_url
        assert asset.storage_file
        assert asset.storage_file.storage.exists(asset.storage_file.name)
        assert (asset.width, asset.height) == (32, 24)
        assert len(asset.content_hash) == 64
        assert asset.source_retrieved_at is not None
        assert asset.status == MediaStatus.NEEDS_REVIEW
        assert asset.reviewed_at is None
        assert asset.published_at is None
        assert "editorial approval is still required" in stdout.getvalue()


@pytest.mark.django_db
def test_finland_media_bootstrap_is_idempotent_and_does_not_redownload_existing_bytes(
    finland,
    monkeypatch,
    tmp_path,
):
    payload = _jpeg_bytes()
    calls = 0

    def fake_download(self, media_url, max_bytes=10 * 1024 * 1024):
        nonlocal calls
        calls += 1
        return DownloadedMedia(
            data=payload,
            filename="Helsinki_tram.jpg",
            mime_type="image/jpeg",
        )

    monkeypatch.setattr(
        "apps.media.management.commands.seed_finland_editorial_media."
        "WikimediaCommonsClient.download_media",
        fake_download,
    )

    with override_settings(MEDIA_ROOT=tmp_path):
        call_command("seed_finland_editorial_media", download=True)
        first_pk = MediaAsset.objects.get().pk
        call_command("seed_finland_editorial_media", download=True)

    assert MediaAsset.objects.count() == 1
    assert MediaAsset.objects.get().pk == first_pk
    assert calls == 1


@pytest.mark.django_db
def test_finland_media_bootstrap_does_not_overwrite_protected_editorial_asset(finland):
    spec = FINLAND_COUNTRY_HERO
    asset = MediaAsset.objects.create(
        source_kind=spec.source_kind,
        external_id=spec.external_id,
        country=finland,
        role=spec.role,
        kind=spec.kind,
        title="Editor approved title",
        status=MediaStatus.APPROVED,
    )
    stdout = StringIO()

    call_command("seed_finland_editorial_media", stdout=stdout)

    asset.refresh_from_db()
    assert asset.title == "Editor approved title"
    assert asset.status == MediaStatus.APPROVED
    assert "PROTECTED" in stdout.getvalue()
