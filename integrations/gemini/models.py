from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class ProviderUsage:
    input_tokens: int | None = None
    output_tokens: int | None = None
    total_tokens: int | None = None


@dataclass(frozen=True, slots=True)
class StructuredGeneration:
    data: dict[str, Any]
    provider_model: str
    response_id: str | None
    usage: ProviderUsage
