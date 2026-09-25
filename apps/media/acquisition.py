from __future__ import annotations

from dataclasses import dataclass
from http.client import HTTPException
from pathlib import PurePosixPath
from urllib.error import HTTPError, URLError
from urllib.parse import unquote, urlsplit
from urllib.request import Request, urlopen

from apps.media.validation import MAX_MEDIA_BYTES

_ALLOWED_DOWNLOAD_HOSTS = frozenset({"upload.wikimedia.org"})
_ALLOWED_CONTENT_TYPES = frozenset({"image/jpeg", "image/png", "image/webp"})


class MediaAcquisitionError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class DownloadedMedia:
    data: bytes
    filename: str
    content_type: str
    final_url: str


def _validate_download_url(url: str) -> str:
    parsed = urlsplit(url)
    if (
        parsed.scheme != "https"
        or parsed.hostname not in _ALLOWED_DOWNLOAD_HOSTS
        or parsed.username is not None
        or parsed.password is not None
        or parsed.query
        or parsed.fragment
    ):
        raise MediaAcquisitionError(
            "Curated media download URL must be credential-free HTTPS on an approved host."
        )

    path = PurePosixPath(unquote(parsed.path))
    filename = path.name
    if not filename or path.suffix.casefold() not in {".jpg", ".jpeg", ".png", ".webp"}:
        raise MediaAcquisitionError("Curated media download URL must identify a supported raster.")
    return filename


def download_media_bytes(
    url: str,
    *,
    timeout_seconds: float = 10.0,
    max_bytes: int = MAX_MEDIA_BYTES,
) -> DownloadedMedia:
    if not 0 < timeout_seconds <= 30:
        raise ValueError("Media acquisition timeout must be > 0 and <= 30 seconds.")
    if max_bytes <= 0:
        raise ValueError("Media acquisition byte limit must be positive.")

    filename = _validate_download_url(url)
    request = Request(
        url,
        headers={
            "Accept": "image/jpeg,image/png,image/webp",
            "User-Agent": "CulturalCurrencyConverter/0.1 curated-media-ingestion",
        },
    )

    try:
        with urlopen(request, timeout=timeout_seconds) as response:
            final_url = str(response.geturl())
            final_filename = _validate_download_url(final_url)
            content_type = str(response.headers.get_content_type()).casefold()
            if content_type not in _ALLOWED_CONTENT_TYPES:
                raise MediaAcquisitionError(
                    f"Curated media returned unsupported content type {content_type or 'unknown'}."
                )

            raw_length = response.headers.get("Content-Length")
            if raw_length:
                try:
                    declared_length = int(raw_length)
                except ValueError as exc:
                    raise MediaAcquisitionError(
                        "Curated media returned an invalid Content-Length header."
                    ) from exc
                if declared_length < 0 or declared_length > max_bytes:
                    raise MediaAcquisitionError(
                        "Curated media exceeds the configured byte-size limit."
                    )

            data = response.read(max_bytes + 1)
    except HTTPError as exc:
        raise MediaAcquisitionError(
            f"Curated media source returned HTTP {exc.code}."
        ) from exc
    except (URLError, HTTPException, TimeoutError) as exc:
        raise MediaAcquisitionError("Curated media download failed.") from exc

    if len(data) > max_bytes:
        raise MediaAcquisitionError("Curated media exceeds the configured byte-size limit.")
    if not data:
        raise MediaAcquisitionError("Curated media source returned an empty body.")

    return DownloadedMedia(
        data=data,
        filename=final_filename or filename,
        content_type=content_type,
        final_url=final_url,
    )
