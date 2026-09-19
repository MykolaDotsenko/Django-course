from django.shortcuts import render

from .presentation.media_preview import build_media_preview_context


def media_preview(request):
    """Render the DEBUG-only Quiet Atlas media QA surface."""

    return render(
        request,
        "design/media_preview.html",
        build_media_preview_context(),
    )
