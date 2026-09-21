from __future__ import annotations

import io

import pytest
from PIL import Image

from apps.media.validation import MediaValidationError, validate_raster_image


def _image_bytes(*, format: str = "PNG", size=(16, 12), color=(10, 20, 30)) -> bytes:
    output = io.BytesIO()
    Image.new("RGB", size, color).save(output, format=format)
    return output.getvalue()


def test_valid_raster_is_decoded_and_hashed_from_bytes():
    result = validate_raster_image(_image_bytes(), filename="example.png")

    assert result.format == "PNG"
    assert result.mime_type == "image/png"
    assert result.width == 16
    assert result.height == 12
    assert result.aspect_ratio == "16 / 12"
    assert len(result.content_hash) == 64


def test_svg_is_rejected_before_public_media_ingestion():
    with pytest.raises(MediaValidationError, match="SVG"):
        validate_raster_image(
            b'<svg xmlns="http://www.w3.org/2000/svg"><script>alert(1)</script></svg>',
            filename="unsafe.svg",
        )


def test_fake_filename_extension_is_rejected():
    jpeg = _image_bytes(format="JPEG")

    with pytest.raises(MediaValidationError, match="extension"):
        validate_raster_image(jpeg, filename="pretend.png")


def test_oversized_payload_is_rejected_before_decode():
    with pytest.raises(MediaValidationError, match="byte-size"):
        validate_raster_image(b"x" * 101, filename="x.png", max_bytes=100)


def test_unknown_bytes_are_rejected():
    with pytest.raises(MediaValidationError, match="decodable"):
        validate_raster_image(b"not-an-image", filename="broken.png")
