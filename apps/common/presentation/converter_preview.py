from __future__ import annotations


def build_converter_preview_context() -> dict[str, object]:
    """Return deterministic illustrative data for the converter component QA surface."""

    return {
        "preview_disclaimer": "Illustrative component data · not a rate quote.",
        "amount_default": {
            "id": "preview-amount",
            "name": "amount",
            "label": "Amount",
            "value": "100.00",
            "placeholder": "0.00",
            "currency_code": "EUR",
            "hint": "Use a decimal point or comma. Thousands separators are not required.",
            "error": "",
        },
        "amount_error": {
            "id": "preview-amount-error",
            "name": "amount_error",
            "label": "Amount",
            "value": "abc",
            "placeholder": "0.00",
            "currency_code": "EUR",
            "hint": "",
            "error": "Enter an amount such as 1234.56 or 1234,56.",
        },
        "source_selection": {
            "id": "preview-source",
            "role_label": "From",
            "country_name": "Finland",
            "currency_name": "Euro",
            "currency_code": "EUR",
            "media_text": "FI",
            "historical": False,
        },
        "destination_selection": {
            "id": "preview-destination",
            "role_label": "To",
            "country_name": "Japan",
            "currency_name": "Japanese yen",
            "currency_code": "JPY",
            "media_text": "JP",
            "historical": False,
        },
        "historical_selection": {
            "id": "preview-historical",
            "role_label": "Historical currency",
            "country_name": "Finland",
            "currency_name": "Finnish markka",
            "currency_code": "FIM",
            "media_text": "FI",
            "historical": True,
        },
        "reference_result": {
            "id": "preview-reference-result",
            "input_amount": "100",
            "input_currency": "EUR",
            "output_amount": "17,450",
            "output_currency": "JPY",
            "status": {
                "kind": "reference",
                "label": "Reference rate",
            },
            "rate_meta": {
                "rate_line": "1 EUR = 174.50 JPY",
                "data_class": "Reference rate",
                "effective_date": "18 Sep 2026",
                "provider": "Frankfurter",
                "fetched_at": "",
                "explanation": (
                    "Reference data is informational. A payment provider may use a different "
                    "rate or add fees."
                ),
            },
        },
        "cached_result": {
            "id": "preview-cached-result",
            "input_amount": "100",
            "input_currency": "EUR",
            "output_amount": "17,450",
            "output_currency": "JPY",
            "status": {
                "kind": "cached",
                "label": "Cached",
            },
            "rate_meta": {
                "rate_line": "1 EUR = 174.50 JPY",
                "data_class": "Cached reference",
                "effective_date": "18 Sep 2026",
                "provider": "Frankfurter",
                "fetched_at": "19 Sep 2026 · 08:12 UTC",
                "explanation": (
                    "The latest refresh is unavailable. This sample demonstrates how preserved "
                    "reference data remains visibly dated."
                ),
            },
        },
    }
