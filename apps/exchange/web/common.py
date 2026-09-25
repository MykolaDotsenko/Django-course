from __future__ import annotations

from django.http import HttpRequest


def is_htmx(request: HttpRequest) -> bool:
    return bool(request.htmx)


def is_history_restore(request: HttpRequest) -> bool:
    return bool(request.htmx.history_restore_request)
