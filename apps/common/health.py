from __future__ import annotations

import logging

from django.db import DatabaseError, connection
from django.http import HttpRequest, JsonResponse
from django.views.decorators.http import require_safe

logger = logging.getLogger("cultural_currency.health")


@require_safe
def health_live(request: HttpRequest) -> JsonResponse:
    """Report process liveness without touching database or external services."""

    return JsonResponse({"status": "ok"})


@require_safe
def health_ready(request: HttpRequest) -> JsonResponse:
    """Report readiness using only dependencies required to serve safely."""

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except DatabaseError:
        logger.warning("readiness_failed", extra={"error_code": "database_unavailable"})
        return JsonResponse(
            {
                "status": "unavailable",
                "checks": {"database": "unavailable"},
            },
            status=503,
        )

    return JsonResponse(
        {
            "status": "ok",
            "checks": {"database": "ok"},
        }
    )
