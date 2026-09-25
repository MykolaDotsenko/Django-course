from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ImageViewModel:
    src: str
    ratio: str
    alt: str
    decorative: bool
    kind: str
    label: str
    width: int
    height: int
    caption: str = ""
    attribution_text: str = ""
    source_url: str = ""
    authenticity_label: str = ""
    srcset: str = ""
    sizes: str = ""
