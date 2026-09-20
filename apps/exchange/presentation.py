from __future__ import annotations

from decimal import Decimal

from django.utils.formats import date_format

from apps.exchange.domain import ConversionResult
from apps.exchange.forms import CurrentConversionForm

_THEME_BY_COUNTRY = {
    "FI": "fi",
    "JP": "jp",
}


def _decimal_text(value: Decimal) -> str:
    text = format(value, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text or "0"


def _money_text(value: Decimal, *, minor_units: int) -> str:
    return f"{value:.{minor_units}f}"


def _selected_value(form: CurrentConversionForm, field_name: str) -> str:
    value = form[field_name].value()
    return str(value or "").upper()


def _selection_context(form: CurrentConversionForm, side: str) -> dict[str, str]:
    country_code = _selected_value(form, f"{side}_country")
    currency_code = _selected_value(form, f"{side}_currency")
    country = form.country_for_code(country_code)
    currency = form.currency_for_code(currency_code)

    return {
        "country_code": country.iso2 if country else "",
        "country_name": country.name if country else "No country context",
        "currency_code": currency.code if currency else currency_code,
        "currency_name": currency.name if currency else "Choose currency",
        "theme": _THEME_BY_COUNTRY.get(country.iso2, "") if country else "",
    }


def build_result_component(
    result: ConversionResult,
    *,
    form: CurrentConversionForm,
) -> dict[str, object]:
    base_currency = form.currency_for_code(result.quote.base_currency)
    quote_currency = form.currency_for_code(result.quote.quote_currency)
    base_minor_units = base_currency.minor_units if base_currency else 2
    quote_minor_units = quote_currency.minor_units if quote_currency else 2

    same_currency = result.quote.base_currency == result.quote.quote_currency
    provider_keys = ", ".join(key.upper() for key in result.quote.provider_keys)
    if same_currency:
        provider = "Exact same-currency rate"
        data_class = "Exact 1:1"
        explanation = "The currencies are identical, so no external rate request is required."
    else:
        provider = "Frankfurter"
        if provider_keys:
            provider = f"{provider} · {provider_keys}"
        data_class = "Cached reference" if result.stale else "Reference rate"
        explanation = (
            "A cached reference quote is being used because a fresh provider response is "
            "temporarily unavailable."
            if result.stale
            else "Reference exchange-rate data is informational; payment providers may use "
            "different rates or add fees."
        )

    effective_date = None if same_currency else date_format(result.quote.effective_date, "j M Y")
    fetched_at = None if same_currency else result.quote.fetched_at.strftime("%d %b %Y · %H:%M UTC")
    input_text = _money_text(result.input_amount, minor_units=base_minor_units)
    output_text = _money_text(result.output_amount, minor_units=quote_minor_units)
    rate_text = _decimal_text(result.quote.rate)

    return {
        "id": "current-conversion-result",
        "input_amount": input_text,
        "input_currency": result.quote.base_currency,
        "output_amount": output_text,
        "output_currency": result.quote.quote_currency,
        "exact": same_currency,
        "stale": result.stale,
        "status": (
            {"kind": "exact", "label": "Exact 1:1"}
            if same_currency
            else {
                "kind": "cached" if result.stale else "reference",
                "label": "Cached reference" if result.stale else "Reference rate",
            }
        ),
        "rate_meta": {
            "rate_line": (
                f"1 {result.quote.base_currency} = {rate_text} {result.quote.quote_currency}"
            ),
            "data_class": data_class,
            "effective_date": effective_date,
            "provider": provider,
            "fetched_at": fetched_at,
            "explanation": explanation,
        },
        "announcement": (
            (
                f"{input_text} {result.quote.base_currency} remains "
                f"{output_text} {result.quote.quote_currency}. "
                "No exchange-rate lookup was required."
            )
            if same_currency
            else (
                f"{input_text} {result.quote.base_currency} is approximately "
                f"{output_text} {result.quote.quote_currency}. "
                f"Reference rate effective {effective_date}."
            )
        ),
    }


def _build_error_summary(form: CurrentConversionForm) -> list[dict[str, str]]:
    if len(form.errors) < 2:
        return []

    summary: list[dict[str, str]] = []
    for field_name, errors in form.errors.items():
        if not errors:
            continue
        if field_name == "__all__":
            summary.append(
                {
                    "href": "#current-conversion-form",
                    "label": "Conversion",
                    "message": str(errors[0]),
                }
            )
            continue

        bound_field = form[field_name]
        summary.append(
            {
                "href": f"#{bound_field.id_for_label}",
                "label": bound_field.label,
                "message": str(errors[0]),
            }
        )
    return summary


def build_converter_context(
    form: CurrentConversionForm,
    *,
    result: ConversionResult | None = None,
    conversion_error: dict[str, str] | None = None,
    validation_attempted: bool = False,
) -> dict[str, object]:
    return {
        "form": form,
        "source": _selection_context(form, "source"),
        "destination": _selection_context(form, "destination"),
        "result_component": build_result_component(result, form=form) if result else None,
        "conversion_error": conversion_error,
        "error_summary": _build_error_summary(form) if validation_attempted else [],
        "has_result": result is not None,
        "reference_data_ready": form.reference_data_ready,
    }
