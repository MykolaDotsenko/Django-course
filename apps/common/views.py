from django.conf import settings
from django.http import Http404
from django.shortcuts import render

from .presentation.converter_preview import build_converter_preview_context
from .presentation.media_preview import build_media_preview_context


def media_preview(request):
    """Render the Quiet Atlas media QA surface only when DEBUG is enabled."""

    if not settings.DEBUG:
        raise Http404

    return render(
        request,
        "design/media_preview.html",
        build_media_preview_context(),
    )


def shell_preview(request):
    """Render the Quiet Atlas shell foundation only when DEBUG is enabled."""

    if not settings.DEBUG:
        raise Http404

    return render(request, "design/shell_preview.html")


def converter_preview(request):
    """Render converter component anatomy only when DEBUG is enabled."""

    if not settings.DEBUG:
        raise Http404

    return render(
        request,
        "design/converter_preview.html",
        build_converter_preview_context(),
    )
