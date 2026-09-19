from django.conf import settings
from django.http import Http404
from django.shortcuts import render

from .presentation.media_preview import build_media_preview_context


def media_preview(request):
    """Render the Quiet Atlas QA surface only when DEBUG is enabled."""

    if not settings.DEBUG:
        raise Http404

    return render(
        request,
        "design/media_preview.html",
        build_media_preview_context(),
    )
