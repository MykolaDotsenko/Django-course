from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path, PurePosixPath
from typing import TypedDict
from urllib.parse import urlsplit

from django import template
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.templatetags.static import static
from django.utils.html import format_html, format_html_join
from django.utils.safestring import SafeString

register = template.Library()


class ViteManifestError(ImproperlyConfigured):
    """Raised when the Vite asset bridge cannot satisfy its rendering contract."""


class ManifestChunk(TypedDict, total=False):
    file: str
    src: str
    isEntry: bool
    imports: list[str]
    css: list[str]


Manifest = dict[str, ManifestChunk]


def _validate_relative_path(value: str, *, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise ViteManifestError(f"{label} must be a non-empty relative path.")

    if any(character in value for character in ("\\", "?", "#")) or "://" in value:
        raise ViteManifestError(f"{label} must be a plain relative POSIX path.")

    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or path.as_posix() != value:
        raise ViteManifestError(f"{label} must be a canonical relative POSIX path.")

    return value


def _dev_server_origin() -> str:
    raw_origin = str(settings.VITE_DEV_SERVER_ORIGIN).strip()
    parsed = urlsplit(raw_origin)

    if (
        parsed.scheme not in {"http", "https"}
        or not parsed.netloc
        or parsed.username is not None
        or parsed.password is not None
        or parsed.path not in {"", "/"}
        or parsed.query
        or parsed.fragment
    ):
        raise ViteManifestError(
            "VITE_DEV_SERVER_ORIGIN must be an http(s) origin without credentials, path, "
            "query or fragment."
        )

    return f"{parsed.scheme}://{parsed.netloc}"


@lru_cache(maxsize=4)
def _load_manifest(manifest_path: str) -> Manifest:
    path = Path(manifest_path)

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ViteManifestError(
            f"Vite manifest not found at {path}. Run 'cd frontend && npm run build' "
            "before serving production assets."
        ) from exc
    except (OSError, json.JSONDecodeError) as exc:
        raise ViteManifestError(f"Vite manifest at {path} is unreadable or malformed.") from exc

    if not isinstance(payload, dict):
        raise ViteManifestError("Vite manifest root must be a JSON object.")

    return payload


def _string_list(chunk: ManifestChunk, field: str, *, chunk_key: str) -> tuple[str, ...]:
    value = chunk.get(field)
    if value is None:
        return ()

    if not isinstance(value, list) or any(not isinstance(item, str) or not item for item in value):
        raise ViteManifestError(
            f"Vite manifest chunk {chunk_key!r} has an invalid {field!r} list."
        )

    return tuple(value)


def _require_chunk(manifest: Manifest, key: str) -> ManifestChunk:
    raw_chunk = manifest.get(key)
    if not isinstance(raw_chunk, dict):
        raise ViteManifestError(f"Vite manifest is missing chunk {key!r}.")

    file_name = raw_chunk.get("file")
    if not isinstance(file_name, str) or not file_name:
        raise ViteManifestError(f"Vite manifest chunk {key!r} is missing a valid 'file'.")

    _validate_relative_path(file_name, label=f"Vite output for {key!r}")
    _string_list(raw_chunk, "css", chunk_key=key)
    _string_list(raw_chunk, "imports", chunk_key=key)

    return raw_chunk


def _imported_chunks(manifest: Manifest, entry_key: str) -> list[ManifestChunk]:
    entry = _require_chunk(manifest, entry_key)
    seen = {entry_key}
    imported_chunks: list[ManifestChunk] = []

    def visit(chunk: ManifestChunk, *, parent_key: str) -> None:
        for imported_key in _string_list(chunk, "imports", chunk_key=parent_key):
            if imported_key in seen:
                continue

            seen.add(imported_key)
            imported = _require_chunk(manifest, imported_key)
            visit(imported, parent_key=imported_key)
            imported_chunks.append(imported)

    visit(entry, parent_key=entry_key)
    return imported_chunks


def _deduplicate(values: list[str]) -> list[str]:
    return list(dict.fromkeys(values))


def _static_asset_url(file_name: str) -> str:
    validated = _validate_relative_path(file_name, label="Vite output")
    return static(f"build/{validated}")


def _render_development_asset(entry: str) -> SafeString:
    origin = _dev_server_origin()
    client_url = f"{origin}/@vite/client"
    entry_url = f"{origin}/{entry}"

    return format_html(
        '<script type="module" src="{}"></script>\n'
        '<script type="module" src="{}"></script>',
        client_url,
        entry_url,
    )


def _render_production_asset(entry: str) -> SafeString:
    manifest_path = str(Path(settings.VITE_MANIFEST_PATH))
    manifest = _load_manifest(manifest_path)
    entry_chunk = _require_chunk(manifest, entry)
    imported_chunks = _imported_chunks(manifest, entry)

    css_files = list(_string_list(entry_chunk, "css", chunk_key=entry))
    for imported_chunk in imported_chunks:
        imported_file = str(imported_chunk["file"])
        css_files.extend(_string_list(imported_chunk, "css", chunk_key=imported_file))

    css_urls = [_static_asset_url(file_name) for file_name in _deduplicate(css_files)]
    preload_urls = [_static_asset_url(str(chunk["file"])) for chunk in imported_chunks]
    script_url = _static_asset_url(str(entry_chunk["file"]))

    stylesheet_tags = format_html_join(
        "\n",
        '<link rel="stylesheet" href="{}">',
        ((url,) for url in css_urls),
    )
    script_tag = format_html('<script type="module" src="{}"></script>', script_url)
    preload_tags = format_html_join(
        "\n",
        '<link rel="modulepreload" href="{}">',
        ((url,) for url in preload_urls),
    )

    parts = [part for part in (stylesheet_tags, script_tag, preload_tags) if part]
    return format_html_join("\n", "{}", ((part,) for part in parts))


@register.simple_tag
def vite_asset(entry: str) -> SafeString:
    """Render Vite development tags or production manifest assets for one entry."""

    validated_entry = _validate_relative_path(entry, label="Vite entry")

    if bool(settings.VITE_DEV_SERVER_ENABLED):
        return _render_development_asset(validated_entry)

    return _render_production_asset(validated_entry)
