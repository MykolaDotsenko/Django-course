from __future__ import annotations

from .media_assets import StaticMediaAsset, get_static_media_asset


COUNTRY_MEDIA_KEYS = {
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
}

STORY_MEDIA_KEYS = {
    "market_basket": "story_market_basket",
    "cafe_affordability": "story_cafe_affordability",
    "street_food_affordability": "story_street_food_affordability",
    "transit_affordability": "story_transit_affordability",
    "budget_hotel_affordability": "story_budget_hotel_affordability",
    "euro_transition": "history_euro_transition",
    "finland_markka_1998": "history_finland_markka_1998",
    "then_now": "history_then_now",
}

DEFAULT_COUNTRY_MEDIA_KEY = "fallback_local_value"
DEFAULT_STORY_MEDIA_KEY = "fallback_history"


def _normalise_country_code(country_code: str | None) -> str:
    return (country_code or "").strip().upper()


def _normalise_story_type(story_type: str | None) -> str:
    return (story_type or "").strip().lower()


def select_country_media(country_code: str | None) -> StaticMediaAsset:
    key = COUNTRY_MEDIA_KEYS.get(
        _normalise_country_code(country_code),
        DEFAULT_COUNTRY_MEDIA_KEY,
    )
    return get_static_media_asset(key)


def select_story_media(story_type: str | None) -> StaticMediaAsset:
    key = STORY_MEDIA_KEYS.get(
        _normalise_story_type(story_type),
        DEFAULT_STORY_MEDIA_KEY,
    )
    return get_static_media_asset(key)


def select_home_hero_media() -> StaticMediaAsset:
    return get_static_media_asset("hero_home_global_value")


def select_payment_culture_media() -> StaticMediaAsset:
    return get_static_media_asset("fallback_payment_culture")


def select_rate_provenance_media() -> StaticMediaAsset:
    return get_static_media_asset("trust_rate_provenance")
