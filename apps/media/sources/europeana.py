from __future__ import annotations

import json
from datetime import UTC, datetime
from http.client import HTTPException
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from apps.media.models import MediaSourceKind
from apps.media.sources.base import MediaCandidate, MediaSourceError

EUROPEANA_SEARCH_URL = "https://api.europeana.eu/record/v2/search.json"
MAX_RESPONSE_BYTES = 2 * 1024 * 1024


def _first_text(value: Any) -> str:
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, list):
        for item in value:
            text = _first_text(item)
            if text:
                return text
    return ""


def _first_https(*values: Any) -> str:
    for value in values:
        candidates = value if isinstance(value, list) else (value,)
        for candidate in candidates:
            text = _first_text(candidate)
            if text.startswith("https://"):
                return text
    return ""


def parse_europeana_search_payload(
    payload: Any,
    *,
    retrieved_at: datetime,
) -> tuple[MediaCandidate, ...]:
    if not isinstance(payload, dict) or payload.get("success") is False:
        raise MediaSourceError("Europeana search response indicates failure.")
    items = payload.get("items")
    if not isinstance(items, list):
        raise MediaSourceError("Europeana search response is missing items.")

    candidates: list[MediaCandidate] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        external_id = str(item.get("id") or "").strip()
        title = _first_text(item.get("title"))
        if not external_id or not title:
            continue

        canonical_url = _first_https(item.get("guid"), item.get("edmIsShownAt"))
        media_url = _first_https(item.get("edmIsShownBy"), item.get("edmPreview"))
        if not canonical_url:
            continue

        source_name = _first_text(item.get("dataProvider")) or _first_text(item.get("provider"))
        creator = _first_text(item.get("dcCreator"))
        rights = _first_text(item.get("rights"))
        licence_id = rights.rsplit("/", 1)[-1] if rights else ""
        attribution = " · ".join(part for part in (creator, source_name, rights) if part)

        candidates.append(
            MediaCandidate(
                source_kind=MediaSourceKind.EUROPEANA,
                external_id=external_id,
                title=title,
                source_name=source_name or "Europeana",
                source_url=canonical_url,
                source_media_url=media_url,
                creator=creator,
                licence_id=licence_id,
                licence_url=rights if rights.startswith("https://") else "",
                rights_statement=rights,
                attribution_text=attribution,
                retrieved_at=retrieved_at,
            )
        )
    return tuple(candidates)


class EuropeanaSearchClient:
    def __init__(self, *, api_key: str, timeout_seconds: float = 10.0):
        if not api_key.strip():
            raise ValueError("Europeana API key is required.")
        if not 0 < timeout_seconds <= 30:
            raise ValueError("Europeana timeout must be > 0 and <= 30 seconds.")
        self.api_key = api_key.strip()
        self.timeout_seconds = timeout_seconds

    def search(self, query: str, *, limit: int = 10) -> tuple[MediaCandidate, ...]:
        normalized_query = " ".join(query.split())
        if not normalized_query:
            raise ValueError("Europeana search query is required.")
        if len(normalized_query) > 200:
            raise ValueError("Europeana search query is too long.")
        if not 1 <= limit <= 20:
            raise ValueError("Europeana search limit must be between 1 and 20.")

        params = {
            "wskey": self.api_key,
            "query": normalized_query,
            "rows": str(limit),
            "media": "true",
            "profile": "rich",
        }
        request = Request(
            f"{EUROPEANA_SEARCH_URL}?{urlencode(params)}",
            headers={
                "Accept": "application/json",
                "User-Agent": "CulturalCurrencyConverter/0.1 media-ingestion",
            },
        )
        payload = self._request_json(request)
        return parse_europeana_search_payload(
            payload,
            retrieved_at=datetime.now(UTC),
        )

    def _request_json(self, request: Request) -> Any:
        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                raw = response.read(MAX_RESPONSE_BYTES + 1)
        except HTTPError as exc:
            if exc.code in {401, 403}:
                raise MediaSourceError("Europeana authentication failed.") from exc
            if exc.code == 429:
                raise MediaSourceError("Europeana rate limit reached.") from exc
            raise MediaSourceError(f"Europeana returned HTTP {exc.code}.") from exc
        except (URLError, HTTPException, TimeoutError) as exc:
            raise MediaSourceError("Europeana request failed.") from exc

        if len(raw) > MAX_RESPONSE_BYTES:
            raise MediaSourceError("Europeana response exceeded the size limit.")
        try:
            return json.loads(raw)
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise MediaSourceError("Europeana returned malformed JSON.") from exc
