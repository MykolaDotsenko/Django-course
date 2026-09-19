from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType

from django.templatetags.static import static

from .media_assets import StaticMediaAsset, get_static_media_asset
from .media_view_models import ImageViewModel, build_static_image_view_model


@dataclass(frozen=True, slots=True)
class RasterCandidate:
    key: str
    semantic_asset_key: str
    path: str
    label: str
    generator: str
    generation_job_id: str
    width: int
    height: int


@dataclass(frozen=True, slots=True)
class RasterComparisonViewModel:
    title: str
    semantic_key: str
    canonical: ImageViewModel
    candidate: ImageViewModel
    generator: str
    generation_job_id: str


_candidates = {
    "japan_local_value_ai_v1": RasterCandidate(
        key="japan_local_value_ai_v1",
        semantic_asset_key="country_japan",
        path="images/quiet-atlas/raster/countries-japan-local-value-ai-v1.webp",
        label="Japan local-value AI candidate",
        generator="Z Image",
        generation_job_id="f5646c31-a25c-4abe-9ab5-b83a57668fdf",
        width=560,
        height=420,
    ),
    "trust_rate_provenance_ai_v1": RasterCandidate(
        key="trust_rate_provenance_ai_v1",
        semantic_asset_key="trust_rate_provenance",
        path="images/quiet-atlas/raster/trust-rate-provenance-ai-v1.webp",
        label="Rate provenance AI candidate",
        generator="Z Image",
        generation_job_id="aa52c950-ee69-4c26-882b-c0a37d4aae63",
        width=560,
        height=420,
    ),
}

RASTER_CANDIDATES = MappingProxyType(_candidates)


def _candidate_image(candidate: RasterCandidate) -> ImageViewModel:
    return ImageViewModel(
        src=static(candidate.path),
        ratio="4 / 3",
        alt="",
        decorative=True,
        kind="story",
        label=candidate.label,
        width=candidate.width,
        height=candidate.height,
    )


def build_raster_comparison(
    candidate: RasterCandidate,
) -> RasterComparisonViewModel:
    canonical_asset: StaticMediaAsset = get_static_media_asset(
        candidate.semantic_asset_key,
    )
    return RasterComparisonViewModel(
        title=candidate.label,
        semantic_key=candidate.semantic_asset_key,
        canonical=build_static_image_view_model(canonical_asset),
        candidate=_candidate_image(candidate),
        generator=candidate.generator,
        generation_job_id=candidate.generation_job_id,
    )


def build_all_raster_comparisons() -> tuple[RasterComparisonViewModel, ...]:
    return tuple(build_raster_comparison(candidate) for candidate in RASTER_CANDIDATES.values())
