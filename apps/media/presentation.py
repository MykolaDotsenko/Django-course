from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from apps.common.presentation.media_view_models import ImageViewModel
from apps.countries.models import Country, Currency
from apps.media.models import MediaAsset, MediaStatus
from apps.media.services import select_published_media


@dataclass(frozen=True, slots=True)
class DisplayMediaSelection:
    image: ImageViewModel
    selection_reason: str
    temporal_match_quality: str
    authenticity_class: str
    fallback_level: int = 0


def build_media_asset_image_view_model(asset: MediaAsset) -> ImageViewModel:
    if not asset.is_published or not asset.storage_file:
        raise ValueError("Only published managed media can be rendered.")

    derivatives = list(
        asset.derivatives.filter(
            status=MediaStatus.PUBLISHED,
            storage_file__gt="",
            width__isnull=False,
            height__isnull=False,
        ).order_by("width", "pk")
    )
    fallback = derivatives[-1] if derivatives else asset

    variants = [*derivatives, asset]
    srcset_entries: list[str] = []
    seen_widths: set[int] = set()
    for variant in variants:
        if not variant.storage_file or not variant.width or variant.width in seen_widths:
            continue
        seen_widths.add(variant.width)
        srcset_entries.append(f"{variant.storage_file.url} {variant.width}w")

    return ImageViewModel(
        src=fallback.storage_file.url,
        ratio=asset.aspect_ratio or f"{asset.width} / {asset.height}",
        alt="" if asset.is_decorative else asset.alt_text,
        decorative=asset.is_decorative,
        kind=asset.kind,
        label=asset.title,
        width=fallback.width or asset.width or 1,
        height=fallback.height or asset.height or 1,
        caption=asset.caption,
        attribution_text=asset.attribution_text,
        source_url=asset.source_url,
        authenticity_label=asset.ai_label if asset.generated_by_ai else "",
        srcset=", ".join(srcset_entries) if len(srcset_entries) > 1 else "",
        sizes="(max-width: 58rem) calc(100vw - 2rem), 42rem" if srcset_entries else "",
    )


def select_media_for_display(
    *,
    role: str,
    country: Country | None = None,
    currency: Currency | None = None,
    target_date: date | None = None,
    aspect_ratio: str | None = None,
) -> DisplayMediaSelection | None:
    """Return reviewed managed media, or no image when nothing meets the bar."""

    stored = select_published_media(
        role=role,
        country=country,
        currency=currency,
        target_date=target_date,
        aspect_ratio=aspect_ratio,
    )
    if stored is None:
        return None

    return DisplayMediaSelection(
        image=build_media_asset_image_view_model(stored.asset),
        selection_reason=stored.selection_reason,
        temporal_match_quality=stored.temporal_match_quality,
        authenticity_class=stored.authenticity_class,
        fallback_level=stored.fallback_level,
    )
