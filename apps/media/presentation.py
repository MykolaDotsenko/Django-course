from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from apps.common.presentation.media_selectors import (
    select_country_media,
    select_history_og_media,
    select_home_og_media,
    select_story_media,
)
from apps.common.presentation.media_view_models import (
    ImageViewModel,
    build_static_image_view_model,
)
from apps.countries.models import Country, Currency
from apps.media.models import MediaAsset, MediaRole
from apps.media.services import select_published_media


@dataclass(frozen=True, slots=True)
class DisplayMediaSelection:
    image: ImageViewModel
    selection_reason: str
    temporal_match_quality: str
    authenticity_class: str
    fallback_level: int


def build_media_asset_image_view_model(asset: MediaAsset) -> ImageViewModel:
    if not asset.is_published or not asset.storage_file:
        raise ValueError("Only published managed media can be rendered.")

    return ImageViewModel(
        src=asset.storage_file.url,
        ratio=asset.aspect_ratio or f"{asset.width} / {asset.height}",
        alt="" if asset.is_decorative else asset.alt_text,
        decorative=asset.is_decorative,
        kind=asset.kind,
        label=asset.title,
        width=asset.width or 1,
        height=asset.height or 1,
        caption=asset.caption,
        attribution_text=asset.attribution_text,
        source_url=asset.source_url,
        authenticity_label=asset.ai_label if asset.generated_by_ai else "",
    )


def _static_fallback(role: str, country: Country | None):
    if role in {MediaRole.COUNTRY_HERO, MediaRole.COUNTRY_TEASER}:
        return select_country_media(country.iso2 if country else None)
    if role in {MediaRole.COMPARISON_THEN, MediaRole.COMPARISON_NOW}:
        return select_story_media("then_now")
    if role in {MediaRole.STORY_COVER, MediaRole.STORY_CHAPTER, MediaRole.HISTORICAL_TIMELINE}:
        return select_story_media(None)
    if role == MediaRole.SOCIAL_PREVIEW:
        return select_history_og_media() if country else select_home_og_media()
    return select_country_media(country.iso2 if country else None)


def select_media_for_display(
    *,
    role: str,
    country: Country | None = None,
    currency: Currency | None = None,
    target_date: date | None = None,
    aspect_ratio: str | None = None,
) -> DisplayMediaSelection:
    stored = select_published_media(
        role=role,
        country=country,
        currency=currency,
        target_date=target_date,
        aspect_ratio=aspect_ratio,
    )
    if stored is not None:
        return DisplayMediaSelection(
            image=build_media_asset_image_view_model(stored.asset),
            selection_reason=stored.selection_reason,
            temporal_match_quality=stored.temporal_match_quality,
            authenticity_class=stored.authenticity_class,
            fallback_level=stored.fallback_level,
        )

    fallback = _static_fallback(role, country)
    return DisplayMediaSelection(
        image=build_static_image_view_model(fallback),
        selection_reason="quiet_atlas_static_fallback",
        temporal_match_quality="fallback",
        authenticity_class="release_owned_illustration",
        fallback_level=1,
    )
