from __future__ import annotations

from django.template.loader import render_to_string

from apps.common.presentation.media_view_models import ImageViewModel


def test_generated_media_authenticity_label_is_visible_not_alt_only():
    image = ImageViewModel(
        src="/media/generated/example.webp",
        ratio="4 / 3",
        alt="Editorial illustration of a historical scene",
        decorative=False,
        kind="generated_illustration",
        label="Historical illustration",
        width=1200,
        height=900,
        caption="Illustration based on sourced historical context.",
        authenticity_label="AI-generated editorial illustration · not an archival photograph",
    )

    html = render_to_string("components/media/image_frame.html", {"image": image})

    assert "AI-generated editorial illustration" in html
    assert "qa-media__authenticity" in html
    assert html.count("AI-generated editorial illustration") == 1


def test_sourced_media_attribution_links_to_canonical_source():
    image = ImageViewModel(
        src="/media/sourced/example.webp",
        ratio="4 / 3",
        alt="Archive photograph",
        decorative=False,
        kind="archival_photo",
        label="Archive photograph",
        width=1200,
        height=900,
        attribution_text="Example Archive · CC BY-SA 4.0",
        source_url="https://commons.wikimedia.org/wiki/File:Example.jpg",
    )

    html = render_to_string("components/media/image_frame.html", {"image": image})

    assert "Example Archive · CC BY-SA 4.0" in html
    assert 'href="https://commons.wikimedia.org/wiki/File:Example.jpg"' in html
