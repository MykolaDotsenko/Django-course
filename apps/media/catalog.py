from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from apps.media.models import MediaKind, MediaRole, MediaSourceKind


@dataclass(frozen=True, slots=True)
class EditorialMediaSpec:
    external_id: str
    country_code: str
    role: str
    kind: str
    city: str
    title: str
    alt_text: str
    caption: str
    source_kind: str
    source_name: str
    source_url: str
    source_media_url: str
    creator: str
    licence_id: str
    licence_url: str
    rights_statement: str
    attribution_text: str
    observed_on: date
    focal_x: Decimal
    focal_y: Decimal


FINLAND_COUNTRY_HERO = EditorialMediaSpec(
    external_id="File:Helsinki tram on line 4 on Aleksanterinkatu in May 2026.jpg",
    country_code="FI",
    role=MediaRole.COUNTRY_HERO,
    kind=MediaKind.CONTEMPORARY_PHOTO,
    city="Helsinki",
    title="Helsinki tram on Aleksanterinkatu",
    alt_text=(
        "Modern tram travelling along Aleksanterinkatu in central Helsinki "
        "with pedestrians and city buildings around it."
    ),
    caption="A contemporary Helsinki street scene on Aleksanterinkatu, photographed in May 2026.",
    source_kind=MediaSourceKind.WIKIMEDIA_COMMONS,
    source_name="Wikimedia Commons",
    source_url=(
        "https://commons.wikimedia.org/wiki/"
        "File:Helsinki_tram_on_line_4_on_Aleksanterinkatu_in_May_2026.jpg"
    ),
    source_media_url=(
        "https://upload.wikimedia.org/wikipedia/commons/6/60/"
        "Helsinki_tram_on_line_4_on_Aleksanterinkatu_in_May_2026.jpg"
    ),
    creator="JIP",
    licence_id="CC BY-SA 4.0",
    licence_url="https://creativecommons.org/licenses/by-sa/4.0/",
    rights_statement="Creative Commons Attribution-ShareAlike 4.0 International",
    attribution_text="JIP · Wikimedia Commons · CC BY-SA 4.0",
    observed_on=date(2026, 5, 24),
    focal_x=Decimal("0.540"),
    focal_y=Decimal("0.530"),
)
