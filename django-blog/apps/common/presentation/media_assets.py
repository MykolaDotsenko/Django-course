from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Literal


AssetKind = Literal["hero", "fallback", "country", "story", "history", "trust"]


class UnknownMediaAssetError(KeyError):
    """Raised when presentation code asks for an unknown static media key."""


@dataclass(frozen=True, slots=True)
class StaticMediaAsset:
    key: str
    path: str
    ratio: str
    kind: AssetKind
    label: str
    decorative: bool = True
    alt: str = ""


def _asset(
    key: str,
    filename: str,
    *,
    kind: AssetKind,
    label: str,
    ratio: str = "4 / 3",
) -> StaticMediaAsset:
    return StaticMediaAsset(
        key=key,
        path=f"images/quiet-atlas/{filename}",
        ratio=ratio,
        kind=kind,
        label=label,
    )


_assets = {
    "hero_home_global_value": _asset(
        "hero_home_global_value",
        "hero-home-global-value-v1.svg",
        kind="hero",
        label="Home hero global value",
        ratio="16 / 9",
    ),
    "fallback_local_value": _asset(
        "fallback_local_value",
        "fallback-local-value-generic-v1.svg",
        kind="fallback",
        label="Generic local-value fallback",
    ),
    "fallback_history": _asset(
        "fallback_history",
        "fallback-history-generic-v1.svg",
        kind="fallback",
        label="Generic historical fallback",
    ),
    "fallback_payment_culture": _asset(
        "fallback_payment_culture",
        "fallback-payment-culture-v1.svg",
        kind="fallback",
        label="Payment-culture fallback",
    ),
    "country_finland": _asset(
        "country_finland",
        "countries-finland-local-value-v1.svg",
        kind="country",
        label="Finland local value",
    ),
    "country_japan": _asset(
        "country_japan",
        "countries-japan-local-value-v1.svg",
        kind="country",
        label="Japan local value",
    ),
    "country_usa": _asset(
        "country_usa",
        "countries-usa-local-value-v1.svg",
        kind="country",
        label="United States local value",
    ),
    "country_uk": _asset(
        "country_uk",
        "countries-uk-local-value-v1.svg",
        kind="country",
        label="United Kingdom local value",
    ),
    "country_france": _asset(
        "country_france",
        "countries-france-local-value-v1.svg",
        kind="country",
        label="France local value",
    ),
    "country_italy": _asset(
        "country_italy",
        "countries-italy-local-value-v1.svg",
        kind="country",
        label="Italy local value",
    ),
    "country_thailand": _asset(
        "country_thailand",
        "countries-thailand-local-value-v1.svg",
        kind="country",
        label="Thailand local value",
    ),
    "country_turkey": _asset(
        "country_turkey",
        "countries-turkey-local-value-v1.svg",
        kind="country",
        label="Turkey local value",
    ),
    "country_germany": _asset(
        "country_germany",
        "countries-germany-local-value-v1.svg",
        kind="country",
        label="Germany local value",
    ),
    "country_spain": _asset(
        "country_spain",
        "countries-spain-local-value-v1.svg",
        kind="country",
        label="Spain local value",
    ),
    "history_euro_transition": _asset(
        "history_euro_transition",
        "history-euro-transition-2002-v1.svg",
        kind="history",
        label="Euro transition illustration",
    ),
    "history_finland_markka_1998": _asset(
        "history_finland_markka_1998",
        "history-finland-markka-1998-v1.svg",
        kind="history",
        label="Finland markka era illustration",
    ),
    "history_then_now": _asset(
        "history_then_now",
        "history-then-now-comparison-v1.svg",
        kind="history",
        label="Then and now comparison illustration",
    ),
    "story_market_basket": _asset(
        "story_market_basket",
        "story-market-basket-value-v1.svg",
        kind="story",
        label="Market-basket affordability",
    ),
    "story_cafe_affordability": _asset(
        "story_cafe_affordability",
        "story-cafe-affordability-v1.svg",
        kind="story",
        label="Cafe affordability",
    ),
    "story_street_food_affordability": _asset(
        "story_street_food_affordability",
        "story-street-food-affordability-v1.svg",
        kind="story",
        label="Street-food affordability",
    ),
    "story_transit_affordability": _asset(
        "story_transit_affordability",
        "story-transit-affordability-v1.svg",
        kind="story",
        label="Transit affordability",
    ),
    "story_budget_hotel_affordability": _asset(
        "story_budget_hotel_affordability",
        "story-budget-hotel-affordability-v1.svg",
        kind="story",
        label="Budget-hotel affordability",
    ),
    "trust_rate_provenance": _asset(
        "trust_rate_provenance",
        "trust-rate-provenance-v1.svg",
        kind="trust",
        label="Rate and source provenance",
    ),
}


QUIET_ATLAS_ASSETS = MappingProxyType(_assets)


def get_static_media_asset(key: str) -> StaticMediaAsset:
    """Return one release-owned media asset by semantic key."""

    try:
        return QUIET_ATLAS_ASSETS[key]
    except KeyError as exc:
        raise UnknownMediaAssetError(key) from exc
