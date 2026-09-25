from __future__ import annotations

from datetime import date

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET

from apps.exchange.forms import RATE_MODE_HISTORICAL
from apps.exchange.queries import search_currency_options


@require_GET
def picker_options_view(request: HttpRequest) -> HttpResponse:
    side = request.GET.get("side", "")
    if side not in {"source", "destination"}:
        side = "source"

    query = " ".join(request.GET.get("q", "").split())[:80]
    historical_mode = request.GET.get("rate_mode") == RATE_MODE_HISTORICAL
    raw_requested_date = request.GET.get("requested_date", "")
    selected_date = None
    if historical_mode and raw_requested_date:
        try:
            selected_date = date.fromisoformat(raw_requested_date)
        except ValueError:
            selected_date = None

    preferred_country_code = request.GET.get(f"{side}_country", "").upper().strip()
    preferred_currency_code = request.GET.get(f"{side}_currency", "").upper().strip()
    search_options = search_currency_options(
        query=query,
        historical_mode=historical_mode,
        selected_date=selected_date,
        preferred_country_code=preferred_country_code,
        preferred_currency_code=preferred_currency_code,
    )
    options: list[dict[str, object]] = []
    for option in search_options:
        option_kind = "country" if option.country_context else "currency"
        option_id = (
            f"{side}-country-{option.country_code.lower()}-{option.currency_code.lower()}"
            if option.country_context
            else f"{side}-currency-{option.currency_code.lower()}"
        )
        label = (
            f"{option.country_name} · {option.currency_name}"
            if option.country_context
            else f"{option.currency_name} · {option.currency_code}"
        )
        meta = (
            f"{option.country_code} · {option.currency_code}"
            if option.country_context
            else "Currency only"
        )
        current_selection = (
            option.country_code == preferred_country_code
            and option.currency_code == preferred_currency_code
        )
        if current_selection:
            meta = f"Current selection · {meta}"
        if option.historical:
            meta += " · Historical"

        options.append(
            {
                "id": option_id,
                "kind": option_kind,
                "country_code": option.country_code,
                "country_name": option.country_name,
                "currency_code": option.currency_code,
                "currency_name": option.currency_name,
                "label": label,
                "meta": meta,
                "historical": option.historical,
            }
        )

    return render(
        request,
        "components/converter/picker_results.html",
        {"side": side, "options": options, "query": query},
    )
