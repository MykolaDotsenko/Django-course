from __future__ import annotations

from dataclasses import dataclass

from django.templatetags.static import static

from .media_assets import AssetKind, StaticMediaAsset


@dataclass(frozen=True, slots=True)
class ImageViewModel:
    src: str
    ratio: str
    alt: str
    decorative: bool
    kind: AssetKind
    label: str
    width: int
    height: int


@dataclass(frozen=True, slots=True)
class MediaCardViewModel:
    image: ImageViewModel
    title: str
    summary: str = ""
    href: str = ""
    eyebrow: str = ""
    badge: str = ""


def build_static_image_view_model(
    asset: StaticMediaAsset,
    *,
    meaningful_alt: str | None = None,
) -> ImageViewModel:
    """Convert a static asset into the one media shape templates consume."""

    if meaningful_alt is None:
        decorative = asset.decorative
        alt = "" if decorative else asset.alt
    else:
        alt = meaningful_alt.strip()
        if not alt:
            raise ValueError("meaningful_alt must contain non-whitespace text")
        decorative = False

    return ImageViewModel(
        src=static(asset.path),
        ratio=asset.ratio,
        alt=alt,
        decorative=decorative,
        kind=asset.kind,
        label=asset.label,
        width=asset.width,
        height=asset.height,
    )
