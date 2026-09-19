from __future__ import annotations

from django.test import SimpleTestCase, override_settings


@override_settings(DEBUG=True)
class MediaPreviewViewTests(SimpleTestCase):
    def test_debug_preview_renders_real_media_system(self):
        response = self.client.get("/_design/media/")

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "design/media_preview.html")

        self.assertEqual(len(response.context["explainer_cards"]), 3)
        self.assertEqual(len(response.context["country_cards"]), 10)
        self.assertEqual(len(response.context["story_cards"]), 5)
        self.assertEqual(len(response.context["history_cards"]), 3)

        self.assertContains(response, "Quiet Atlas media system")
        self.assertContains(response, "23 assets")
        self.assertContains(response, "Convert money with context.")
        self.assertContains(response, 'loading="eager"')
        self.assertContains(response, 'fetchpriority="high"')
        self.assertContains(response, 'loading="lazy"')

    def test_preview_exposes_key_visual_qa_scenarios(self):
        response = self.client.get("/_design/media/")

        for text in (
            "Local value",
            "Payment culture",
            "Finland",
            "Japan",
            "Transit affordability",
            "Budget accommodation",
            "Then & Now",
            "Why trust this rate?",
            "Illustrative visual",
        ):
            with self.subTest(text=text):
                self.assertContains(response, text)


class MediaPreviewProductionGuardTests(SimpleTestCase):
    @override_settings(DEBUG=False)
    def test_preview_is_not_available_when_debug_is_disabled(self):
        response = self.client.get("/_design/media/")

        self.assertEqual(response.status_code, 404)
