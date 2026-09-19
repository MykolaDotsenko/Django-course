from __future__ import annotations

from django.contrib.staticfiles import finders
from django.test import SimpleTestCase

from apps.common.presentation.media_assets import (
    QUIET_ATLAS_ASSETS,
    StaticMediaAsset,
    UnknownMediaAssetError,
    get_static_media_asset,
)
from apps.common.presentation.media_selectors import (
    COUNTRY_MEDIA_KEYS,
    STORY_MEDIA_KEYS,
    select_country_media,
    select_history_og_media,
    select_history_then_now_mobile_media,
    select_home_hero_media,
    select_home_hero_mobile_media,
    select_home_og_media,
    select_local_value_og_media,
    select_payment_culture_media,
    select_rate_provenance_media,
    select_story_media,
)
from apps.common.presentation.media_view_models import (
    build_static_image_view_model,
)


class StaticMediaRegistryTests(SimpleTestCase):
    def test_registry_contains_expected_release_pack(self):
        self.assertEqual(len(QUIET_ATLAS_ASSETS), 28)

    def test_registry_keys_match_asset_keys(self):
        for key, asset in QUIET_ATLAS_ASSETS.items():
            with self.subTest(key=key):
                self.assertEqual(asset.key, key)

    def test_paths_are_unique_and_scoped_to_quiet_atlas(self):
        paths = [asset.path for asset in QUIET_ATLAS_ASSETS.values()]

        self.assertEqual(len(paths), len(set(paths)))
        for path in paths:
            with self.subTest(path=path):
                self.assertTrue(path.startswith("images/quiet-atlas/"))
                self.assertTrue(path.endswith(".svg"))

    def test_assets_use_expected_aspect_ratio_by_kind(self):
        expected_ratios = {
            "hero": "16 / 9",
            "fallback": "4 / 3",
            "country": "4 / 3",
            "story": "4 / 3",
            "history": "4 / 3",
            "trust": "4 / 3",
            "responsive": "4 / 5",
            "social": "40 / 21",
        }

        for asset in QUIET_ATLAS_ASSETS.values():
            with self.subTest(key=asset.key):
                self.assertEqual(asset.ratio, expected_ratios[asset.kind])

    def test_release_owned_assets_are_decorative_by_default(self):
        for asset in QUIET_ATLAS_ASSETS.values():
            with self.subTest(key=asset.key):
                self.assertTrue(asset.decorative)
                self.assertEqual(asset.alt, "")

    def test_registry_is_immutable(self):
        with self.assertRaises(TypeError):
            QUIET_ATLAS_ASSETS["unexpected"] = StaticMediaAsset(  # type: ignore[index]
                key="unexpected",
                path="images/quiet-atlas/unexpected.svg",
                ratio="4 / 3",
                kind="fallback",
                label="Unexpected",
                width=1200,
                height=900,
            )

    def test_unknown_key_raises_domain_specific_error(self):
        with self.assertRaises(UnknownMediaAssetError):
            get_static_media_asset("does_not_exist")

    def test_every_registry_path_is_discoverable_by_django_staticfiles(self):
        for asset in QUIET_ATLAS_ASSETS.values():
            with self.subTest(key=asset.key):
                self.assertIsNotNone(
                    finders.find(asset.path),
                    f"Static asset is not discoverable: {asset.path}",
                )


class MediaSelectorTests(SimpleTestCase):
    def test_country_map_covers_expected_initial_destinations(self):
        self.assertEqual(
            COUNTRY_MEDIA_KEYS,
            {
                "FI": "country_finland",
                "JP": "country_japan",
                "US": "country_usa",
                "GB": "country_uk",
                "UK": "country_uk",
                "FR": "country_france",
                "IT": "country_italy",
                "TH": "country_thailand",
                "TR": "country_turkey",
                "DE": "country_germany",
                "ES": "country_spain",
            },
        )

    def test_country_selector_normalises_case_and_whitespace(self):
        self.assertEqual(select_country_media(" fi ").key, "country_finland")
        self.assertEqual(select_country_media("gb").key, "country_uk")

    def test_unknown_or_missing_country_uses_local_value_fallback(self):
        for value in (None, "", "XX"):
            with self.subTest(value=value):
                self.assertEqual(
                    select_country_media(value).key,
                    "fallback_local_value",
                )

    def test_story_map_covers_initial_story_types(self):
        self.assertEqual(
            set(STORY_MEDIA_KEYS),
            {
                "market_basket",
                "cafe_affordability",
                "street_food_affordability",
                "transit_affordability",
                "budget_hotel_affordability",
                "euro_transition",
                "finland_markka_1998",
                "then_now",
            },
        )

    def test_story_selector_normalises_case_and_whitespace(self):
        self.assertEqual(
            select_story_media(" THEN_NOW ").key,
            "history_then_now",
        )

    def test_unknown_or_missing_story_uses_history_fallback(self):
        for value in (None, "", "unknown"):
            with self.subTest(value=value):
                self.assertEqual(
                    select_story_media(value).key,
                    "fallback_history",
                )

    def test_named_selectors_are_explicit(self):
        self.assertEqual(
            select_home_hero_media().key,
            "hero_home_global_value",
        )
        self.assertEqual(
            select_payment_culture_media().key,
            "fallback_payment_culture",
        )
        self.assertEqual(
            select_rate_provenance_media().key,
            "trust_rate_provenance",
        )
        self.assertEqual(
            select_home_hero_mobile_media().key,
            "hero_home_global_value_mobile",
        )
        self.assertEqual(
            select_history_then_now_mobile_media().key,
            "history_then_now_mobile",
        )
        self.assertEqual(
            select_home_og_media().key,
            "og_home_global_value",
        )
        self.assertEqual(
            select_history_og_media().key,
            "og_history_then_now",
        )
        self.assertEqual(
            select_local_value_og_media().key,
            "og_local_value",
        )


class ImageViewModelTests(SimpleTestCase):
    def test_decorative_static_asset_builds_static_url_with_empty_alt(self):
        asset = get_static_media_asset("country_finland")

        image = build_static_image_view_model(asset)

        self.assertEqual(
            image.src,
            "/static/images/quiet-atlas/countries-finland-local-value-v1.svg",
        )
        self.assertEqual(image.ratio, "4 / 3")
        self.assertEqual(image.alt, "")
        self.assertTrue(image.decorative)
        self.assertEqual(image.kind, "country")
        self.assertEqual(image.width, 1200)
        self.assertEqual(image.height, 900)

    def test_hero_exposes_intrinsic_wide_dimensions(self):
        image = build_static_image_view_model(
            get_static_media_asset("hero_home_global_value"),
        )

        self.assertEqual(image.ratio, "16 / 9")
        self.assertEqual(image.width, 1600)
        self.assertEqual(image.height, 900)

    def test_derivatives_expose_expected_intrinsic_dimensions(self):
        mobile = build_static_image_view_model(
            get_static_media_asset("hero_home_global_value_mobile"),
        )
        social = build_static_image_view_model(
            get_static_media_asset("og_home_global_value"),
        )

        self.assertEqual((mobile.width, mobile.height), (960, 1200))
        self.assertEqual(mobile.ratio, "4 / 5")
        self.assertEqual((social.width, social.height), (1200, 630))
        self.assertEqual(social.ratio, "40 / 21")

    def test_meaningful_alt_promotes_asset_to_meaningful_content(self):
        asset = get_static_media_asset("history_then_now")

        image = build_static_image_view_model(
            asset,
            meaningful_alt="Illustration comparing historical and current money context.",
        )

        self.assertFalse(image.decorative)
        self.assertEqual(
            image.alt,
            "Illustration comparing historical and current money context.",
        )

    def test_blank_meaningful_alt_is_rejected(self):
        asset = get_static_media_asset("history_then_now")

        with self.assertRaisesMessage(
            ValueError,
            "meaningful_alt must contain non-whitespace text",
        ):
            build_static_image_view_model(asset, meaningful_alt="   ")
