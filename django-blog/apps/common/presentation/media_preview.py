from __future__ import annotations

from .media_assets import get_static_media_asset
from .media_selectors import (
    select_country_media,
    select_home_hero_media,
    select_payment_culture_media,
    select_rate_provenance_media,
    select_story_media,
)
from .media_view_models import (
    MediaCardViewModel,
    build_static_image_view_model,
)


COUNTRY_PREVIEW = (
    ("FI", "Finland"),
    ("JP", "Japan"),
    ("US", "United States"),
    ("GB", "United Kingdom"),
    ("FR", "France"),
    ("IT", "Italy"),
    ("DE", "Germany"),
    ("ES", "Spain"),
    ("TH", "Thailand"),
    ("TR", "Turkey"),
)

STORY_PREVIEW = (
    (
        "market_basket",
        "Everyday value",
        "Market basket",
        "See how a converted amount translates into practical grocery buying power.",
    ),
    (
        "cafe_affordability",
        "Everyday value",
        "Café affordability",
        "Turn an abstract exchange rate into an intuitive coffee-and-pastry comparison.",
    ),
    (
        "street_food_affordability",
        "Everyday value",
        "Street-food affordability",
        "Compare a familiar amount with simple local meal choices.",
    ),
    (
        "transit_affordability",
        "Mobility",
        "Transit affordability",
        "Understand roughly how much everyday public transport the same amount represents.",
    ),
    (
        "budget_hotel_affordability",
        "Travel budget",
        "Budget accommodation",
        "Add a higher-value spending category without turning the product into a booking site.",
    ),
)


def _image(asset_key: str):
    return build_static_image_view_model(get_static_media_asset(asset_key))


def build_media_preview_context() -> dict[str, object]:
    """Build deterministic data for the DEBUG-only visual QA surface."""

    explainer_cards = (
        MediaCardViewModel(
            image=_image("fallback_local_value"),
            eyebrow="Understand",
            title="Local value",
            summary="Translate a converted amount into familiar everyday purchases.",
            badge="Fallback",
        ),
        MediaCardViewModel(
            image=_image("fallback_history"),
            eyebrow="Explore",
            title="Historical context",
            summary="Compare money across time without hiding requested and effective dates.",
            badge="Illustrative visual",
        ),
        MediaCardViewModel(
            image=build_static_image_view_model(select_payment_culture_media()),
            eyebrow="Travel",
            title="Payment culture",
            summary="Explain cash, card and contactless habits without making the image factual evidence.",
            badge="Fallback",
        ),
    )

    country_cards = tuple(
        MediaCardViewModel(
            image=build_static_image_view_model(select_country_media(code)),
            eyebrow="Destination",
            title=name,
            summary="Country-specific atmosphere with deterministic fallback behavior.",
        )
        for code, name in COUNTRY_PREVIEW
    )

    story_cards = tuple(
        MediaCardViewModel(
            image=build_static_image_view_model(select_story_media(story_type)),
            eyebrow=eyebrow,
            title=title,
            summary=summary,
            badge="Illustrative visual",
        )
        for story_type, eyebrow, title, summary in STORY_PREVIEW
    )

    history_cards = (
        MediaCardViewModel(
            image=build_static_image_view_model(select_story_media("then_now")),
            eyebrow="Historical comparison",
            title="Then & Now",
            summary="A dedicated two-era visual for comparing historical and current money context.",
            badge="Illustrative visual",
        ),
        MediaCardViewModel(
            image=build_static_image_view_model(select_story_media("finland_markka_1998")),
            eyebrow="Currency era",
            title="Finland before the euro",
            summary="Editorial support for a markka-era story without pretending to be archival photography.",
            badge="Illustrative visual",
        ),
        MediaCardViewModel(
            image=build_static_image_view_model(select_story_media("euro_transition")),
            eyebrow="Currency transition",
            title="The euro transition",
            summary="A neutral transition visual that avoids exact fabricated banknote reproduction.",
            badge="Illustrative visual",
        ),
    )

    trust_card = MediaCardViewModel(
        image=build_static_image_view_model(select_rate_provenance_media()),
        eyebrow="Trust",
        title="Why trust this rate?",
        summary="Use source, effective date, freshness and provider metadata as inspectable product information.",
        badge="Source education",
    )

    return {
        "hero_image": build_static_image_view_model(select_home_hero_media()),
        "explainer_cards": explainer_cards,
        "country_cards": country_cards,
        "story_cards": story_cards,
        "history_cards": history_cards,
        "trust_card": trust_card,
    }
