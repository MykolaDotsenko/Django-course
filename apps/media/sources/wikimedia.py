from __future__ import annotations

import html
import json
import re
from datetime import UTC, datetime
from http.client import HTTPException
from typing import Any
from urllib.error import HTTPError, URLError
from pathlib import PurePosixPath
from urllib.parse import quote, unquote, urlencode, urlsplit
from urllib.request import Request, urlopen

from apps.media.models import MediaSourceKind
from apps.media.sources.base import DownloadedMedia, MediaCandidate, MediaSourceError
from apps.media.validation import MAX_MEDIA_BYTES

COMMONS_API_URL = "https://commons.wikimedia.org/w/api.php"
MAX_RESPONSE_BYTES = 2 * 1024 * 1024
_ALLOWED_MEDIA_MIME_TYPES = frozenset({"image/jpeg", "image/png", "image/webp"})
_WIKIMEDIA_MEDIA_HOST = "upload.wikimedia.org"
_TAG_RE = re.compile(r"<[^>]+>")


def _plain_text(value: Any) -> str:
    if isinstance(value, dict):
        value = value.get("value", "")
    text = html.unescape(str(value or ""))
    return " ".join(_TAG_RE.sub(" ", text).split())


def _metadata_value(metadata: Any, key: str) -> str:
    if not isinstance(metadata, dict):
        return ""
    return _plain_text(metadata.get(key))


def parse_wikimedia_search_payload(
    payload: Any,
    *,
    retrieved_at: datetime,
) -> tuple[MediaCandidate, ...]:
    if not isinstance(payload, dict):
        raise MediaSourceError("Wikimedia Commons response must be an object.")
    query = payload.get("query")
    pages = query.get("pages") if isinstance(query, dict) else None
    if not isinstance(pages, list):
        raise MediaSourceError("Wikimedia Commons response is missing page results.")

    candidates: list[MediaCandidate] = []
    for page in pages:
        if not isinstance(page, dict):
            continue
        imageinfo_rows = page.get("imageinfo")
        if not isinstance(imageinfo_rows, list) or not imageinfo_rows:
            continue
        imageinfo = imageinfo_rows[0]
        if not isinstance(imageinfo, dict):
            continue

        mime = str(imageinfo.get("mime") or "")
        media_url = str(imageinfo.get("url") or "").strip()
        if not mime.startswith("image/") or not media_url.startswith("https://"):
            continue

        title = str(page.get("title") or "").removeprefix("File:").strip()
        page_id = str(page.get("pageid") or page.get("title") or "").strip()
        if not title or not page_id:
            continue

        metadata = imageinfo.get("extmetadata")
        creator = _metadata_value(metadata, "Artist")
        credit = _metadata_value(metadata, "Credit")
        licence_id = _metadata_value(metadata, "LicenseShortName")
        licence_url = _metadata_value(metadata, "LicenseUrl")
        rights = _metadata_value(metadata, "UsageTerms") or licence_id
        attribution = " · ".join(part for part in (creator, credit, licence_id) if part)

        canonical_url = str(page.get("canonicalurl") or "").strip()
        if not canonical_url.startswith("https://"):
            canonical_url = "https://commons.wikimedia.org/wiki/" + quote(
                str(page.get("title") or "").replace(" ", "_"), safe=":()_-"
            )

        width = imageinfo.get("width")
        height = imageinfo.get("height")
        candidates.append(
            MediaCandidate(
                source_kind=MediaSourceKind.WIKIMEDIA_COMMONS,
                external_id=page_id,
                title=title,
                source_name="Wikimedia Commons",
                source_url=canonical_url,
                source_media_url=media_url,
                creator=creator,
                licence_id=licence_id,
                licence_url=licence_url if licence_url.startswith("https://") else "",
                rights_statement=rights,
                attribution_text=attribution,
                width=width if isinstance(width, int) and width > 0 else None,
                height=height if isinstance(height, int) and height > 0 else None,
                retrieved_at=retrieved_at,
            )
        )
    return tuple(candidates)


def _validate_wikimedia_media_url(value: str) -> str:
    parsed = urlsplit(value.strip())
    if (
        parsed.scheme != "https"
        or parsed.hostname != _WIKIMEDIA_MEDIA_HOST
        or parsed.username is not None
        or parsed.password is not None
        or parsed.fragment
    ):
        raise MediaSourceError(
            "Wikimedia media URL must be credential-free HTTPS on upload.wikimedia.org."
        )
    return value.strip()


def _response_content_type(response: Any) -> str:
    headers = getattr(response, "headers", None)
    if headers is None:
        return ""

    get_content_type = getattr(headers, "get_content_type", None)
    if callable(get_content_type):
        return str(get_content_type()).lower()

    getter = getattr(headers, "get", None)
    if callable(getter):
        raw = str(getter("Content-Type", "") or "")
        return raw.partition(";")[0].strip().lower()
    return ""


class WikimediaCommonsClient:
    def __init__(self, *, timeout_seconds: float = 10.0):
        if not 0 < timeout_seconds <= 30:
            raise ValueError("Wikimedia timeout must be > 0 and <= 30 seconds.")
        self.timeout_seconds = timeout_seconds

    def search(self, query: str, *, limit: int = 10) -> tuple[MediaCandidate, ...]:
        normalized_query = " ".join(query.split())
        if not normalized_query:
            raise ValueError("Wikimedia search query is required.")
        if len(normalized_query) > 200:
            raise ValueError("Wikimedia search query is too long.")
        if not 1 <= limit <= 20:
            raise ValueError("Wikimedia search limit must be between 1 and 20.")

        params = {
            "action": "query",
            "format": "json",
            "formatversion": "2",
            "generator": "search",
            "gsrsearch": normalized_query,
            "gsrnamespace": "6",
            "gsrlimit": str(limit),
            "prop": "info|imageinfo",
            "inprop": "url",
            "iiprop": "url|mime|size|extmetadata",
            "iiextmetadatafilter": (
                "LicenseShortName|LicenseUrl|Artist|Credit|ImageDescription|UsageTerms"
            ),
            "iiextmetadatalanguage": "en",
        }
        request = Request(
            f"{COMMONS_API_URL}?{urlencode(params)}",
            headers={
                "Accept": "application/json",
                "User-Agent": "CulturalCurrencyConverter/0.1 media-ingestion",
            },
        )
        payload = self._request_json(request)
        return parse_wikimedia_search_payload(
            payload,
            retrieved_at=datetime.now(UTC),
        )

    def download_media(
        self,
        media_url: str,
        *,
        max_bytes: int = MAX_MEDIA_BYTES,
    ) -> DownloadedMedia:
        if not 1 <= max_bytes <= MAX_MEDIA_BYTES:
            raise ValueError("Wikimedia media max_bytes must be within the managed-media limit.")

        validated_url = _validate_wikimedia_media_url(media_url)
        request = Request(
            validated_url,
            headers={
                "Accept": "image/jpeg,image/png,image/webp",
                "User-Agent": "CulturalCurrencyConverter/0.1 media-ingestion",
            },
        )

        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                final_url = _validate_wikimedia_media_url(
                    str(response.geturl() if hasattr(response, "geturl") else validated_url)
                )
                content_type = _response_content_type(response)
                if content_type not in _ALLOWED_MEDIA_MIME_TYPES:
                    raise MediaSourceError(
                        "Wikimedia media response used an unsupported content type."
                    )

                headers = getattr(response, "headers", None)
                raw_length = headers.get("Content-Length") if hasattr(headers, "get") else None
                if raw_length:
                    try:
                        declared_length = int(raw_length)
                    except (TypeError, ValueError) as exc:
                        raise MediaSourceError(
                            "Wikimedia media response has an invalid Content-Length."
                        ) from exc
                    if declared_length < 0 or declared_length > max_bytes:
                        raise MediaSourceError(
                            "Wikimedia media response exceeded the managed-media byte limit."
                        )

                raw = response.read(max_bytes + 1)
        except MediaSourceError:
            raise
        except HTTPError as exc:
            raise MediaSourceError(f"Wikimedia media returned HTTP {exc.code}.") from exc
        except (URLError, HTTPException, TimeoutError) as exc:
            raise MediaSourceError("Wikimedia media download failed.") from exc

        if len(raw) > max_bytes:
            raise MediaSourceError("Wikimedia media response exceeded the managed-media byte limit.")

        filename = PurePosixPath(unquote(urlsplit(final_url).path)).name
        if not filename:
            raise MediaSourceError("Wikimedia media URL is missing a filename.")

        return DownloadedMedia(
            data=raw,
            filename=filename,
            mime_type=content_type,
        )

    def _request_json(self, request: Request) -> Any:
        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                raw = response.read(MAX_RESPONSE_BYTES + 1)
        except HTTPError as exc:
            raise MediaSourceError(f"Wikimedia Commons returned HTTP {exc.code}.") from exc
        except (URLError, HTTPException, TimeoutError) as exc:
            raise MediaSourceError("Wikimedia Commons request failed.") from exc

        if len(raw) > MAX_RESPONSE_BYTES:
            raise MediaSourceError("Wikimedia Commons response exceeded the size limit.")
        try:
            return json.loads(raw)
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise MediaSourceError("Wikimedia Commons returned malformed JSON.") from exc
