from __future__ import annotations

import logging
from urllib.parse import urlencode

from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.cache import patch_vary_headers
from django.views.decorators.http import require_GET, require_http_methods

from apps.countries.models import CountryCurrency, Currency
from apps.exchange.cache import LatestQuoteGateway
from apps.exchange.config import load_fx_runtime_config
from apps.exchange.forms import CurrentConversionForm
from apps.exchange.presentation import build_converter_context
from apps.exchange.providers.base import (
    FxProviderError,
    FxProviderInvalidPayload,
    FxProviderUnavailable,
    FxProviderUnsupportedPair,
)
from apps.exchange.services import quote_conversion

logger = logging.getLogger("cultural_currency.exchange")


def build_latest_quote_gateway() -> LatestQuoteGateway:
    config = load_fx_runtime_config()
    return LatestQuoteGateway(config.build_provider())


def _is_htmx(request: HttpRequest) -> bool:
    return request.headers.get("HX-Request", "").lower() == "true"


def _is_history_restore(request: HttpRequest) -> bool:
    return request.headers.get("HX-History-Restore-Request", "").lower() == "true"


def _country_for_currency(currency_code: str, *, preferred: str = "") -> str:
    links = CountryCurrency.objects.current().filter(currency__code=currency_code).primary()
    if preferred:
        preferred_match = (
            links.filter(country__iso2=preferred).values_list("country__iso2", flat=True).first()
        )
        if preferred_match:
            return preferred_match
    return links.values_list("country__iso2", flat=True).first() or ""


def _default_initial() -> dict[str, str]:
    currency_codes = list(
        Currency.objects.filter(is_active=True).order_by("code").values_list("code", flat=True)
    )
    if not currency_codes:
        return {"amount": "100.00"}

    source_currency = "EUR" if "EUR" in currency_codes else currency_codes[0]
    destination_currency = (
        "JPY"
        if "JPY" in currency_codes
        else next((code for code in currency_codes if code != source_currency), source_currency)
    )
    return {
        "amount": "100.00",
        "source_country": _country_for_currency(source_currency, preferred="FI"),
        "source_currency": source_currency,
        "destination_country": _country_for_currency(destination_currency, preferred="JP"),
        "destination_currency": destination_currency,
    }


def _canonical_conversion_url(form: CurrentConversionForm) -> str:
    cleaned = form.cleaned_data
    params = {
        "convert": "1",
        "amount": format(cleaned["amount_decimal"], "f"),
        "source_country": cleaned.get("source_country", ""),
        "source_currency": cleaned["source_currency"],
        "destination_country": cleaned.get("destination_country", ""),
        "destination_currency": cleaned["destination_currency"],
    }
    return f"{reverse('converter')}?{urlencode(params)}"


def _swap_payload(request: HttpRequest):
    payload = request.POST.copy()
    payload["source_country"], payload["destination_country"] = (
        payload.get("destination_country", ""),
        payload.get("source_country", ""),
    )
    payload["source_currency"], payload["destination_currency"] = (
        payload.get("destination_currency", ""),
        payload.get("source_currency", ""),
    )
    return payload


def _conversion_error(exc: FxProviderError) -> dict[str, str]:
    if isinstance(exc, FxProviderUnsupportedPair):
        return {
            "title": "This currency pair is not available.",
            "detail": "Choose another supported currency pair and try again.",
        }
    if isinstance(exc, FxProviderInvalidPayload):
        return {
            "title": "The rate source returned unusable data.",
            "detail": "No conversion was shown. Try again in a moment.",
        }
    if isinstance(exc, FxProviderUnavailable):
        return {
            "title": "Reference rates are temporarily unavailable.",
            "detail": "Your selections are preserved. Try the conversion again shortly.",
        }
    return {
        "title": "The conversion could not be completed.",
        "detail": "Your selections are preserved. Try again.",
    }


@require_http_methods(["GET", "POST"])
def converter(request: HttpRequest) -> HttpResponse:
    convert_requested = False

    if request.method == "POST":
        swapping = request.POST.get("action") == "swap"
        data = _swap_payload(request) if swapping else request.POST
        form = CurrentConversionForm(data)
        convert_requested = not swapping or request.POST.get("conversion_active") == "1"
    else:
        convert_requested = request.GET.get("convert") == "1"
        form = (
            CurrentConversionForm(request.GET)
            if convert_requested
            else CurrentConversionForm(initial=_default_initial())
        )

    result = None
    error = None
    form_valid = form.is_valid() if convert_requested else False
    if form_valid:
        cleaned = form.cleaned_data
        quote_currency = form.currency_for_code(cleaned["destination_currency"])
        try:
            result = quote_conversion(
                amount=cleaned["amount_decimal"],
                base_currency=cleaned["source_currency"],
                quote_currency=cleaned["destination_currency"],
                quote_minor_units=quote_currency.minor_units if quote_currency else 2,
                gateway=build_latest_quote_gateway(),
            )
        except FxProviderError as exc:
            logger.warning(
                "FX conversion provider failure",
                extra={
                    "provider": "frankfurter",
                    "error_code": exc.__class__.__name__,
                },
            )
            error = _conversion_error(exc)

    if request.method == "POST" and not _is_htmx(request) and result is not None:
        return redirect(_canonical_conversion_url(form))

    context = build_converter_context(form, result=result, conversion_error=error)
    fragment = _is_htmx(request) and not _is_history_restore(request)
    template = "components/converter/current_panel.html" if fragment else "pages/converter.html"
    response = render(request, template, context)
    patch_vary_headers(response, ["HX-Request"])

    if fragment and result is not None:
        response["HX-Push-Url"] = _canonical_conversion_url(form)
    return response


@require_GET
def picker_options(request: HttpRequest) -> HttpResponse:
    side = request.GET.get("side", "")
    if side not in {"source", "destination"}:
        side = "source"

    query = " ".join(request.GET.get("q", "").split())[:80]
    currency_filter = Currency.objects.filter(is_active=True)
    links = CountryCurrency.objects.current().select_related("country", "currency")

    if query:
        from django.db.models import Q

        currency_filter = currency_filter.filter(
            Q(code__icontains=query) | Q(name__icontains=query)
        )
        links = links.filter(
            Q(country__iso2__icontains=query)
            | Q(country__name__icontains=query)
            | Q(currency__code__icontains=query)
            | Q(currency__name__icontains=query)
        )

    options: list[dict[str, str]] = []
    for currency in currency_filter.order_by("code")[:8]:
        options.append(
            {
                "id": f"{side}-currency-{currency.code.lower()}",
                "country_code": "",
                "country_name": "",
                "currency_code": currency.code,
                "currency_name": currency.name,
                "label": f"{currency.name} · {currency.code}",
                "meta": "Currency only",
            }
        )

    seen = {(option["country_code"], option["currency_code"]) for option in options}
    for link in links.order_by("country__name", "currency__code")[:16]:
        identity = (link.country.iso2, link.currency.code)
        if identity in seen:
            continue
        seen.add(identity)
        options.append(
            {
                "id": (f"{side}-country-{link.country.iso2.lower()}-{link.currency.code.lower()}"),
                "country_code": link.country.iso2,
                "country_name": link.country.name,
                "currency_code": link.currency.code,
                "currency_name": link.currency.name,
                "label": f"{link.country.name} · {link.currency.name}",
                "meta": f"{link.country.iso2} · {link.currency.code}",
            }
        )
        if len(options) >= 20:
            break

    return render(
        request,
        "components/converter/picker_results.html",
        {"side": side, "options": options, "query": query},
    )
