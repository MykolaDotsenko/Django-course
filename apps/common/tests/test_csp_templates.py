from __future__ import annotations

import re
from pathlib import Path

from django.conf import settings

_INLINE_EVENT_HANDLER = re.compile(r"\son[a-z][a-z0-9_-]*\s*=", re.IGNORECASE)
_SCRIPT_TAG = re.compile(r"<script\b(?P<attrs>[^>]*)>", re.IGNORECASE)
_JS_HTMX_VALUE = re.compile(r"hx-vals\s*=\s*[\"']\s*js:", re.IGNORECASE)

_ALLOWED_INLINE_STYLE_TEMPLATES = {
    "components/media/image_frame.html",
}


def _project_templates() -> list[Path]:
    root = Path(settings.BASE_DIR) / "templates"
    return sorted(root.rglob("*.html"))


def test_project_templates_remain_compatible_with_strict_public_script_csp() -> None:
    violations: list[str] = []

    for path in _project_templates():
        relative = path.relative_to(Path(settings.BASE_DIR) / "templates").as_posix()
        text = path.read_text(encoding="utf-8")

        for match in _SCRIPT_TAG.finditer(text):
            if "src=" not in match.group("attrs").casefold():
                violations.append(f"{relative}: inline <script>")

        if _INLINE_EVENT_HANDLER.search(text):
            violations.append(f"{relative}: inline event handler")
        if "javascript:" in text.casefold():
            violations.append(f"{relative}: javascript: URL")
        if "hx-on" in text.casefold():
            violations.append(f"{relative}: hx-on inline script")
        if _JS_HTMX_VALUE.search(text):
            violations.append(f"{relative}: hx-vals js: expression")

    assert violations == []


def test_inline_style_surface_is_explicit_and_does_not_expand_silently() -> None:
    templates_with_inline_style: set[str] = set()

    for path in _project_templates():
        text = path.read_text(encoding="utf-8").casefold()
        if " style=" in text:
            templates_with_inline_style.add(
                path.relative_to(Path(settings.BASE_DIR) / "templates").as_posix()
            )

    assert templates_with_inline_style == _ALLOWED_INLINE_STYLE_TEMPLATES


def test_htmx_indicator_styles_are_externalized_for_strict_style_csp() -> None:
    root = Path(settings.BASE_DIR)
    base_template = (root / "templates/base.html").read_text(encoding="utf-8")
    converter_css = (
        root / "frontend/src/styles/current-converter.css"
    ).read_text(encoding="utf-8")

    assert '{"includeIndicatorStyles": false}' in base_template
    assert ".htmx-indicator" in converter_css
    assert ".htmx-request .htmx-indicator" in converter_css
