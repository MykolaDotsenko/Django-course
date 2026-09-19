from __future__ import annotations

from django.template.loader import render_to_string
from django.test import SimpleTestCase

from apps.common.presentation.media_assets import get_static_media_asset
from apps.common.presentation.media_view_models import (
    MediaCardViewModel,
    build_static_image_view_model,
)


class ImageFrameTemplateTests(SimpleTestCase):
    def test_decorative_image_defaults_to_lazy_async_loading(self):
        image = build_static_image_view_model(
            get_static_media_asset("country_finland"),
        )

        html = render_to_string(
            "components/media/image_frame.html",
            {"image": image},
        )

        self.assertIn('loading="lazy"', html)
        self.assertIn('decoding="async"', html)
        self.assertIn('aria-hidden="true"', html)
        self.assertIn('alt=""', html)
        self.assertIn('width="1200"', html)
        self.assertIn('height="900"', html)
        self.assertNotIn("fetchpriority=", html)

    def test_hero_can_be_eager_and_high_priority(self):
        image = build_static_image_view_model(
            get_static_media_asset("hero_home_global_value"),
        )

        html = render_to_string(
            "components/media/image_frame.html",
            {
                "image": image,
                "loading": "eager",
                "fetchpriority": "high",
            },
        )

        self.assertIn('loading="eager"', html)
        self.assertIn('fetchpriority="high"', html)
        self.assertIn('width="1600"', html)
        self.assertIn('height="900"', html)

    def test_meaningful_image_is_not_hidden_from_accessibility_tree(self):
        image = build_static_image_view_model(
            get_static_media_asset("history_then_now"),
            meaningful_alt="Illustration comparing past and present money context.",
        )

        html = render_to_string(
            "components/media/image_frame.html",
            {"image": image},
        )

        self.assertIn(
            'alt="Illustration comparing past and present money context."',
            html,
        )
        self.assertNotIn('aria-hidden="true"', html)

    def test_caption_is_optional_and_rendered_semantically(self):
        image = build_static_image_view_model(
            get_static_media_asset("history_then_now"),
        )

        html = render_to_string(
            "components/media/image_frame.html",
            {
                "image": image,
                "caption": "Illustrative visual — not an archival photograph.",
            },
        )

        self.assertIn("<figcaption", html)
        self.assertIn(
            "Illustrative visual — not an archival photograph.",
            html,
        )


class MediaCardTemplateTests(SimpleTestCase):
    def setUp(self):
        self.image = build_static_image_view_model(
            get_static_media_asset("country_japan"),
        )

    def test_card_renders_optional_content_and_link(self):
        html = render_to_string(
            "components/media/media_card.html",
            {
                "card": MediaCardViewModel(
                    image=self.image,
                    eyebrow="Local value",
                    title="Japan",
                    summary="See what everyday spending feels like locally.",
                    href="/countries/jp/",
                    badge="Featured",
                ),
            },
        )

        self.assertIn("Local value", html)
        self.assertIn('href="/countries/jp/"', html)
        self.assertIn(">Japan</a>", html)
        self.assertIn(
            "See what everyday spending feels like locally.",
            html,
        )
        self.assertIn("Featured", html)
        self.assertIn('loading="lazy"', html)

    def test_card_renders_title_without_link_when_href_is_missing(self):
        html = render_to_string(
            "components/media/media_card.html",
            {
                "card": MediaCardViewModel(
                    image=self.image,
                    title="Japan",
                ),
            },
        )

        self.assertIn("Japan", html)
        self.assertNotIn("<a ", html)
