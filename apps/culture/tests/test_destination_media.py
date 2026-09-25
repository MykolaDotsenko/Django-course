from __future__ import annotations

import io
import tempfile
from pathlib import Path

import pytest
from django.db import DatabaseError
from django.template.loader import render_to_string
from django.test import override_settings
from PIL import Image

from apps.common.presentation.media_view_models import ImageViewModel
from apps.countries.models import Country
from apps.culture.media import select_destination_hero_image
from apps.media.models import MediaAsset, MediaKind, MediaRole, MediaSourceKind
from apps.media.services import approve_media_asset, attach_media_bytes, publish_media_asset


def _png(*, size=(64, 48), color=(20, 80, 120)) -> bytes:
    output = io.BytesIO()
    Image.new("RGB", size, color).save(output, format="PNG")
    return output.getvalue()


@pytest.fixture
def media_root():
    with tempfile.TemporaryDirectory() as directory:
        with override_settings(MEDIA_ROOT=Path(directory)):
            yield Path(directory)


def _hero_asset(finland: Country) -> MediaAsset:
    return MediaAsset.objects.create(
        kind=MediaKind.CONTEMPORARY_PHOTO,
        source_kind=MediaSourceKind.WIKIMEDIA_COMMONS,
        role=MediaRole.COUNTRY_HERO,
        country=finland,
        city="Helsinki",
        title="Helsinki tram",
        alt_text="A Helsinki tram on a central city street.",
        caption="Helsinki tram in May 2026.",
        source_name="Wikimedia Commons",
        source_url="https://commons.wikimedia.org/wiki/File:Helsinki.png",
        source_media_url="https://upload.wikimedia.org/Helsinki.png",
        creator="Creator",
        licence_id="CC BY-SA 4.0",
        licence_url="https://creativecommons.org/licenses/by-sa/4.0/",
        rights_statement="Creative Commons Attribution-ShareAlike 4.0 International",
        attribution_text="Creator · CC BY-SA 4.0",
    )


@pytest.mark.django_db
def test_destination_hero_uses_only_published_managed_media(media_root) -> None:
    finland = Country.objects.create(iso2="FI", iso3="FIN", name="Finland")
    asset = _hero_asset(finland)

    assert select_destination_hero_image("FI") is None

    attach_media_bytes(asset, _png(), filename="Helsinki.png")
    approve_media_asset(asset)
    publish_media_asset(asset)

    image = select_destination_hero_image("fi")

    assert image is not None
    assert image.src.startswith("/media/sourced/")
    assert image.alt == "A Helsinki tram on a central city street."
    assert image.caption == "Helsinki tram in May 2026."
    assert image.attribution_text == "Creator · CC BY-SA 4.0"
    assert image.source_url == "https://commons.wikimedia.org/wiki/File:Helsinki.png"


@pytest.mark.django_db
def test_destination_hero_media_failure_is_optional(
    monkeypatch,
) -> None:
    Country.objects.create(iso2="FI", iso3="FIN", name="Finland")

    def unavailable(*args, **kwargs):
        raise DatabaseError("media lookup failed")

    monkeypatch.setattr("apps.culture.media.select_media_for_display", unavailable)

    assert select_destination_hero_image("FI") is None


def test_destination_context_template_renders_reviewed_hero_with_provenance() -> None:
    image = ImageViewModel(
        src="/media/sourced/helsinki.webp",
        ratio="4 / 3",
        alt="A Helsinki tram on Aleksanterinkatu.",
        decorative=False,
        kind=MediaKind.CONTEMPORARY_PHOTO,
        label="Helsinki tram",
        width=1600,
        height=1200,
        caption="Helsinki tram, May 2026.",
        attribution_text="JIP · CC BY-SA 4.0",
        source_url="https://commons.wikimedia.org/wiki/File:Helsinki.jpg",
    )
    component = {
        "country_name": "Finland",
        "hero_image": image,
        "historical_notice": None,
        "show_explore_nav": False,
        "prices": [],
        "payment": None,
    }

    html = render_to_string(
        "components/culture/destination_context.html",
        {"component": component},
    )

    assert 'class="qa-destination-context__hero"' in html
    assert 'style="aspect-ratio: 16 / 9;"' in html
    assert 'loading="lazy"' in html
    assert "A Helsinki tram on Aleksanterinkatu." in html
    assert "Helsinki tram, May 2026." in html
    assert "JIP · CC BY-SA 4.0" in html
    assert 'href="https://commons.wikimedia.org/wiki/File:Helsinki.jpg"' in html
    assert "fetchpriority=" not in html
