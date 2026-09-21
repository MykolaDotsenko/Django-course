from __future__ import annotations

import logging
from datetime import date
from decimal import Decimal
from urllib.parse import urlencode

from django.conf import settings
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.cache import patch_vary_headers
from django.views.decorators.http import require_GET, require_http_methods

from apps.countries.models import CountryCurrency, Currency
from apps.countries.services import historical_currency_suggestion
from apps.exchange.ai.service import build_runtime_explanation_service
from apps.exchange.ai.tokens import ExplanationTokenError, load_conversion_explanation_token
from apps.exchange.cache import HistoricalQuoteGateway, HistoricalSeriesGateway, LatestQuoteGateway
from apps.exchange.config import load_fx_runtime_config
from apps.exchange.domain import (
    ConversionResult,
    HistoricalCoverageReason,
    HistoricalCurrencyMetadata,
    HistoricalObservationUnavailable,
    HistoricalOutOfCoverage,
    RateQuote,
    RateSeriesRangeError,
    convert_amount,
)
from apps.exchange.forms import (
    RATE_MODE_HISTORICAL,
    CurrentConversionForm,
    HistoricalSeriesForm,
)
from apps.exchange.presentation import build_converter_context
from apps.exchange.providers.base import (
    FxProviderError,
    FxProviderInvalidPayload,
    FxProviderUnavailable,
    FxProviderUnsupportedPair,
)
from apps.exchange.series_presentation import (
    build_rate_series_component,
    build_then_now_component,
)
from apps.exchange.services import (
    compare_historical_to_latest,
    get_rate_series,
    quote_conversion,
    quote_historical_conversion,
)

logger = logging.getLogger("cultural_currency.exchange")


def build_latest_quote_gateway() -> LatestQuoteGateway:
    config = load_fx_runtime_config()
    return LatestQuoteGateway(config.build_provider())


def build_historical_quote_gateway() -> HistoricalQuoteGateway:
    config = load_fx_runtime_config()
    return HistoricalQuoteGateway(config.build_provider())


def build_historical_series_gateway() -> HistoricalSeriesGateway:
    config = load_fx_runtime_config()
    return HistoricalSeriesGateway(config.build_provider())


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
    if cleaned.get("rate_mode") == RATE_MODE_HISTORICAL:
        params["rate_mode"] = RATE_MODE_HISTORICAL
        params["requested_date"] = cleaned["requested_date"].isoformat()
    return f"{reverse('converter')}?{urlencode(params)}"


def _historical_currency_metadata(currency: Currency | None) -> HistoricalCurrencyMetadata | None:
    if currency is None:
        return None
    return HistoricalCurrencyMetadata(
        code=currency.code,
        active_from=currency.active_from,
        active_to=currency.active_to,
        coverage_from=currency.coverage_from,
        coverage_to=currency.coverage_to,
        coverage_to_is_terminal=currency.coverage_to_is_terminal,
    )


def _historical_currency_payload(request: HttpRequest):
    value = request.POST.get("historical_currency_action", "")
    try:
        side, currency_code = value.split(":", 1)
    except ValueError:
        return request.POST
    if side not in {"source", "destination"}:
        return request.POST

    payload = request.POST.copy()
    payload[f"{side}_currency"] = currency_code.upper()
    return payload


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


def _conversion_error(
    exc: FxProviderError | HistoricalObservationUnavailable | HistoricalOutOfCoverage,
    *,
    historical: bool = False,
) -> dict[str, str]:
    if isinstance(exc, HistoricalOutOfCoverage):
        boundary = exc.boundary.strftime("%d %b %Y")
        if exc.reason is HistoricalCoverageReason.CURRENCY_NOT_YET_ACTIVE:
            detail = (
                f"{exc.currency_code} was not yet active on the selected date. "
                f"Known lifecycle starts {boundary}."
            )
        elif exc.reason is HistoricalCoverageReason.CURRENCY_RETIRED:
            detail = (
                f"{exc.currency_code} was already retired on the selected date. "
                f"Known lifecycle ends {boundary}."
            )
        elif exc.reason is HistoricalCoverageReason.PROVIDER_COVERAGE_NOT_STARTED:
            detail = (
                f"The rate source has no {exc.currency_code} observations that far back. "
                f"Known provider coverage starts {boundary}."
            )
        else:
            detail = (
                f"The rate source has no {exc.currency_code} observations that late. "
                f"Known provider coverage ends {boundary}."
            )
        return {
            "title": "The selected date is outside known historical coverage.",
            "detail": detail,
        }
    if isinstance(exc, HistoricalObservationUnavailable):
        return {
            "title": "No nearby historical observation is available.",
            "detail": (
                "No published observation falls within the allowed window for this dataset's "
                "observation frequency. Choose another date."
            ),
        }
    if isinstance(exc, HistoricalObservationUnavailable):
        return 422, {
            "title": "Historical trend cannot confirm the selected observation.",
            "detail": (
                "The selected normalized quote is outside the accepted observation window. "
                "The original conversion remains intact."
            ),
        }
    if isinstance(exc, FxProviderUnsupportedPair):
        if historical:
            return {
                "title": "No historical observation is available for this pair and date.",
                "detail": (
                    "Try another date or currency pair. Historical provider coverage can differ "
                    "from current coverage."
                ),
            }
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

    conversion_active = False

    if request.method == "POST":
        swapping = request.POST.get("action") == "swap"
        using_historical_currency = bool(request.POST.get("historical_currency_action"))
        conversion_active = request.POST.get("conversion_active") == "1"
        if using_historical_currency:
            data = _historical_currency_payload(request)
        elif swapping:
            data = _swap_payload(request)
        else:
            data = request.POST
        form = CurrentConversionForm(data)
        convert_requested = using_historical_currency or not swapping or conversion_active
    else:
        convert_requested = request.GET.get("convert") == "1"
        form = (
            CurrentConversionForm(request.GET)
            if convert_requested
            else CurrentConversionForm(initial=_default_initial())
        )

    result = None
    error = None
    historical_suggestions = []
    response_status = 200
    form_valid = form.is_valid() if convert_requested else False
    if form_valid:
        cleaned = form.cleaned_data
        base_currency = form.currency_for_code(cleaned["source_currency"])
        quote_currency = form.currency_for_code(cleaned["destination_currency"])
        historical = cleaned.get("rate_mode") == RATE_MODE_HISTORICAL
        if historical:
            for side in ("source", "destination"):
                suggestion = historical_currency_suggestion(
                    country_code=cleaned.get(f"{side}_country", ""),
                    selected_currency_code=cleaned[f"{side}_currency"],
                    selected_date=cleaned["requested_date"],
                )
                if suggestion is not None:
                    historical_suggestions.append((side, suggestion))
        try:
            if historical:
                result = quote_historical_conversion(
                    amount=cleaned["amount_decimal"],
                    base_currency=cleaned["source_currency"],
                    quote_currency=cleaned["destination_currency"],
                    quote_minor_units=quote_currency.minor_units if quote_currency else 2,
                    requested_date=cleaned["requested_date"],
                    gateway=build_historical_quote_gateway,
                    base_metadata=_historical_currency_metadata(base_currency),
                    quote_metadata=_historical_currency_metadata(quote_currency),
                )
            else:
                result = quote_conversion(
                    amount=cleaned["amount_decimal"],
                    base_currency=cleaned["source_currency"],
                    quote_currency=cleaned["destination_currency"],
                    quote_minor_units=quote_currency.minor_units if quote_currency else 2,
                    gateway=build_latest_quote_gateway(),
                )
        except (FxProviderError, HistoricalObservationUnavailable, HistoricalOutOfCoverage) as exc:
            if isinstance(
                exc,
                (
                    FxProviderUnsupportedPair,
                    HistoricalObservationUnavailable,
                    HistoricalOutOfCoverage,
                ),
            ):
                response_status = 422
            elif isinstance(exc, FxProviderInvalidPayload):
                response_status = 502
            else:
                response_status = 503

            logger.warning(
                "FX conversion provider failure",
                extra={
                    "provider": "frankfurter",
                    "error_code": exc.__class__.__name__,
                },
            )
            error = _conversion_error(exc, historical=historical)

    if convert_requested and not form_valid and request.method == "POST":
        response_status = 422

    if request.method == "POST" and not _is_htmx(request) and result is not None:
        return redirect(_canonical_conversion_url(form))

    preserve_previous_result = (
        _is_htmx(request)
        and conversion_active
        and result is None
        and response_status in {422, 502, 503}
    )
    context = build_converter_context(
        form,
        result=result,
        conversion_error=error,
        validation_attempted=convert_requested,
        conversion_active=conversion_active,
        preserve_previous_result=preserve_previous_result,
        historical_currency_suggestions=historical_suggestions,
    )
    fragment = _is_htmx(request) and not _is_history_restore(request)
    template = "components/converter/current_panel.html" if fragment else "pages/converter.html"
    response = render(request, template, context, status=response_status)
    patch_vary_headers(response, ["HX-Request", "HX-History-Restore-Request"])

    if fragment and result is not None:
        response["HX-Push-Url"] = _canonical_conversion_url(form)
    return response


@require_GET
def picker_options(request: HttpRequest) -> HttpResponse:
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

    currency_filter = (
        Currency.objects.all() if historical_mode else Currency.objects.filter(is_active=True)
    )
    if historical_mode and selected_date is not None:
        links = CountryCurrency.objects.on_date(selected_date).select_related("country", "currency")
    elif historical_mode:
        links = CountryCurrency.objects.select_related("country", "currency")
    else:
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


def _build_then_now_enrichment(cleaned, series_result):
    base_currency = Currency.objects.filter(code=cleaned["base"]).first()
    quote_currency = Currency.objects.filter(code=cleaned["quote"]).first()
    if base_currency is None or quote_currency is None:
        return None, "Latest comparison is unavailable because currency metadata is incomplete."

    amount = cleaned.get("amount_decimal")
    comparison_amount_error = cleaned.get("comparison_amount_error")

    historical_amount = amount if amount is not None else Decimal("1")
    requested_date = cleaned.get("requested_date") or cleaned["selected_date"]
    exact_series_point = next(
        (
            point
            for point in series_result.series.points
            if point.observation_date == cleaned["selected_date"]
        ),
        None,
    )
    if exact_series_point is None:
        return (
            None,
            "Then & Now comparison is unavailable because the selected observation "
            "is not present in the loaded series.",
        )

    historical_quote = RateQuote(
        base_currency=series_result.series.base_currency,
        quote_currency=series_result.series.quote_currency,
        rate=exact_series_point.rate,
        requested_date=requested_date,
        effective_date=exact_series_point.observation_date,
        fetched_at=series_result.series.fetched_at,
        provider_policy=series_result.series.provider_policy,
        provider_keys=exact_series_point.provider_keys,
        historical=True,
        observation_granularity=series_result.series.observation_granularity,
    )
    historical = ConversionResult(
        input_amount=historical_amount,
        output_amount=convert_amount(
            historical_amount,
            historical_quote,
            minor_units=quote_currency.minor_units,
        ),
        quote=historical_quote,
        stale=series_result.stale,
    )

    if comparison_amount_error:
        return None, comparison_amount_error
    if amount is None:
        return None, None

    inactive = [
        currency.code for currency in (base_currency, quote_currency) if not currency.is_active
    ]
    if inactive:
        codes = ", ".join(inactive)
        return (
            None,
            f"Latest reference comparison is not shown because {codes} is archived "
            "and has no current-market interpretation.",
        )

    try:
        latest = quote_conversion(
            amount=amount,
            base_currency=cleaned["base"],
            quote_currency=cleaned["quote"],
            quote_minor_units=quote_currency.minor_units,
            gateway=build_latest_quote_gateway(),
        )
    except FxProviderError:
        return (
            None,
            "Latest reference comparison is temporarily unavailable. "
            "The historical trend remains valid.",
        )

    comparison = compare_historical_to_latest(historical, latest)
    return (
        build_then_now_component(
            comparison,
            base_minor_units=base_currency.minor_units,
            quote_minor_units=quote_currency.minor_units,
        ),
        None,
    )


def _series_error(exc: Exception) -> tuple[int, dict[str, str]]:
    if isinstance(exc, (RateSeriesRangeError, HistoricalOutOfCoverage)):
        return 422, {
            "title": "Choose a supported historical range.",
            "detail": str(exc),
        }
    if isinstance(exc, FxProviderUnsupportedPair):
        return 422, {
            "title": "Historical series is unavailable for this pair.",
            "detail": "Single-date conversion remains available when the selected observation is supported.",
        }
    if isinstance(exc, FxProviderInvalidPayload):
        return 502, {
            "title": "The rate source returned unusable historical series data.",
            "detail": "Single-date conversion remains intact. Try the trend again later.",
        }
    return 503, {
        "title": "Historical series is unavailable.",
        "detail": "Single-date conversion remains intact. Try the trend again later.",
    }


@require_GET
def historical_series(request: HttpRequest) -> HttpResponse:
    form = HistoricalSeriesForm(request.GET)
    component = None
    error = None
    response_status = 200

    if form.is_valid():
        cleaned = form.cleaned_data
        try:
            result = get_rate_series(
                base_currency=cleaned["base"],
                quote_currency=cleaned["quote"],
                start_date=cleaned["start_date_resolved"],
                end_date=cleaned["end_date_resolved"],
                gateway=build_historical_series_gateway,
            )
            then_now, comparison_notice = _build_then_now_enrichment(cleaned, result)
            component = build_rate_series_component(
                result,
                selected_date=cleaned["selected_date"],
                requested_date=cleaned.get("requested_date"),
                period=cleaned["period"],
                amount=cleaned.get("amount_decimal"),
                then_now=then_now,
                comparison_notice=comparison_notice,
            )
        except (
            RateSeriesRangeError,
            HistoricalObservationUnavailable,
            HistoricalOutOfCoverage,
            FxProviderError,
        ) as exc:
            response_status, error = _series_error(exc)
    else:
        response_status = 422
        error = {
            "title": "Choose a valid historical trend range.",
            "detail": "Check the pair, selected observation date and range controls.",
        }

    context = {
        "series_form": form,
        "series_component": component,
        "series_error": error,
    }
    if _is_htmx(request):
        return render(
            request,
            "components/converter/rate_series.html",
            context,
            status=response_status,
        )
    return render(
        request,
        "pages/historical_series.html",
        context,
        status=response_status,
    )


@require_http_methods(["POST"])
def conversion_explanation(request: HttpRequest) -> HttpResponse:
    if not settings.AI_RUNTIME_EXPLANATION_ENABLED:
        raise Http404("Runtime AI explanation is disabled.")

    token = request.POST.get("explanation_token", "")
    explanation = None
    explanation_error = None
    response_status = 200

    try:
        snapshot = load_conversion_explanation_token(token)
    except ExplanationTokenError:
        response_status = 422
        explanation_error = {
            "title": "This explanation request is no longer valid.",
            "detail": "Run the conversion again, then choose Explain this.",
        }
    else:
        service = build_runtime_explanation_service()
        delivery = service.explain(snapshot)
        explanation = {
            "result": delivery.result,
            "cache_status": delivery.cache_status,
        }

    context = {
        "explanation": explanation,
        "explanation_error": explanation_error,
    }
    fragment = request.headers.get("HX-Request") == "true"
    template = (
        "components/converter/explanation.html" if fragment else "pages/conversion_explanation.html"
    )
    response = render(request, template, context, status=response_status)
    patch_vary_headers(response, ["HX-Request"])
    return response
