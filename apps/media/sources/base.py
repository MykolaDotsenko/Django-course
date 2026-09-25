from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


class MediaSourceError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class DownloadedMedia:
    data: bytes = field(repr=False)
    filename: str
    mime_type: str


@dataclass(frozen=True, slots=True)
class MediaCandidate:
    source_kind: str
    external_id: str
    title: str
    source_name: str
    source_url: str
    source_media_url: str = ""
    creator: str = ""
    licence_id: str = ""
    licence_url: str = ""
    rights_statement: str = ""
    attribution_text: str = ""
    width: int | None = None
    height: int | None = None
    retrieved_at: datetime | None = None
