from __future__ import annotations

import hashlib
import io
import warnings
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, UnidentifiedImageError

MAX_MEDIA_BYTES = 10 * 1024 * 1024
MAX_MEDIA_PIXELS = 40_000_000
MAX_MEDIA_DIMENSION = 12_000
ALLOWED_RASTER_FORMATS = frozenset({"JPEG", "PNG", "WEBP"})
_EXTENSION_FORMATS = {
    ".jpg": "JPEG",
    ".jpeg": "JPEG",
    ".png": "PNG",
    ".webp": "WEBP",
}


class MediaValidationError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class ValidatedImage:
    format: str
    mime_type: str
    width: int
    height: int
    content_hash: str

    @property
    def aspect_ratio(self) -> str:
        return f"{self.width} / {self.height}"


def _looks_like_svg(data: bytes) -> bool:
    prefix = data[:2048].lstrip().lower()
    return prefix.startswith(b"<?xml") or b"<svg" in prefix


def validate_raster_image(
    data: bytes,
    *,
    filename: str = "",
    max_bytes: int = MAX_MEDIA_BYTES,
) -> ValidatedImage:
    if not data:
        raise MediaValidationError("Media file is empty.")
    if len(data) > max_bytes:
        raise MediaValidationError("Media file exceeds the configured byte-size limit.")
    if _looks_like_svg(data):
        raise MediaValidationError(
            "Third-party SVG is rejected; sanitize or rasterize it before managed-media ingestion."
        )

    previous_max_pixels = Image.MAX_IMAGE_PIXELS
    Image.MAX_IMAGE_PIXELS = MAX_MEDIA_PIXELS
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            try:
                with Image.open(io.BytesIO(data)) as image:
                    image_format = (image.format or "").upper()
                    width, height = image.size
                    frames = getattr(image, "n_frames", 1)
                    image.verify()
            except (UnidentifiedImageError, OSError, Image.DecompressionBombError) as exc:
                raise MediaValidationError("Media bytes are not a safe decodable raster image.") from exc
            except Image.DecompressionBombWarning as exc:
                raise MediaValidationError("Media image exceeds the safe pixel-count limit.") from exc
    finally:
        Image.MAX_IMAGE_PIXELS = previous_max_pixels

    if image_format not in ALLOWED_RASTER_FORMATS:
        raise MediaValidationError(
            f"Unsupported raster image format {image_format or 'unknown'}."
        )
    if width <= 0 or height <= 0:
        raise MediaValidationError("Media image dimensions must be positive.")
    if width > MAX_MEDIA_DIMENSION or height > MAX_MEDIA_DIMENSION:
        raise MediaValidationError("Media image exceeds the maximum supported dimension.")
    if width * height > MAX_MEDIA_PIXELS:
        raise MediaValidationError("Media image exceeds the safe pixel-count limit.")
    if frames != 1:
        raise MediaValidationError("Animated images are not accepted as editorial media.")

    suffix = Path(filename).suffix.lower()
    if suffix:
        expected_format = _EXTENSION_FORMATS.get(suffix)
        if expected_format is None:
            raise MediaValidationError("Media filename uses an unsupported extension.")
        if expected_format != image_format:
            raise MediaValidationError("Media filename extension does not match the decoded image.")

    mime_type = Image.MIME.get(image_format)
    if not mime_type or not mime_type.startswith("image/"):
        raise MediaValidationError("Decoded media does not have a supported image MIME type.")

    return ValidatedImage(
        format=image_format,
        mime_type=mime_type,
        width=width,
        height=height,
        content_hash=hashlib.sha256(data).hexdigest(),
    )
