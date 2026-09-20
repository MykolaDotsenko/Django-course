from __future__ import annotations

from urllib.parse import urlencode

from django.urls import reverse
from django.utils.formats import date_format

from apps.exchange.domain import RateSeriesResult


def _rate_text(value) -> str:
    text = format(value, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text or "0"


def _series_url(
    *,
    base: str,
    quote: str,
    selected_date,
    requested_date,
    period: str,
    start_date=None,
    end_date=None,
) -> str:
    params = {
        "base": base,
        "quote": quote,
        "selected_date": selected_date.isoformat(),
        "period": period,
    }
    if requested_date is not None:
        params["requested_date"] = requested_date.isoformat()
    if start_date is not None:
        params["start_date"] = start_date.isoformat()
    if end_date is not None:
        params["end_date"] = end_date.isoformat()
    return f"{reverse('historical_series')}?{urlencode(params)}"


def build_rate_series_component(
    result: RateSeriesResult,
    *,
    selected_date,
    requested_date=None,
    period: str,
) -> dict[str, object]:
    series = result.series
    points = [
        {
            "date": point.observation_date,
            "date_label": date_format(point.observation_date, "j M Y"),
            "date_iso": point.observation_date.isoformat(),
            "rate": _rate_text(point.rate),
            "selected": point.observation_date == selected_date,
            "provider_keys": ", ".join(key.upper() for key in point.provider_keys),
        }
        for point in series.points
    ]

    minimum = series.minimum_point
    maximum = series.maximum_point
    last = series.points[-1] if series.points else None
    selected_point = next(
        (point for point in series.points if point.observation_date == selected_date),
        None,
    )
    provider_keys = sorted(
        {
            key.upper()
            for point in series.points
            for key in point.provider_keys
        }
    )

    period_links = []
    for key, label in (("1y", "1Y"), ("5y", "5Y"), ("10y", "10Y")):
        period_links.append(
            {
                "key": key,
                "label": label,
                "active": period == key,
                "url": _series_url(
                    base=series.base_currency,
                    quote=series.quote_currency,
                    selected_date=selected_date,
                    requested_date=requested_date,
                    period=key,
                ),
            }
        )

    summary = (
        "No published observations are available in this range."
        if not series.points
        else (
            f"{len(series.points)} published observations from "
            f"{date_format(series.points[0].observation_date, 'j M Y')} to "
            f"{date_format(series.points[-1].observation_date, 'j M Y')}. "
            f"The observed range was {_rate_text(minimum.rate)} to "
            f"{_rate_text(maximum.rate)} {series.quote_currency} per "
            f"{series.base_currency}."
        )
    )

    return {
        "id": "historical-trend",
        "pair": f"{series.base_currency} → {series.quote_currency}",
        "base_currency": series.base_currency,
        "quote_currency": series.quote_currency,
        "selected_date": selected_date,
        "selected_date_label": date_format(selected_date, "j M Y"),
        "requested_date": requested_date,
        "requested_date_label": (
            date_format(requested_date, "j M Y") if requested_date is not None else None
        ),
        "period": period,
        "period_links": period_links,
        "start_date": series.start_date,
        "start_date_iso": series.start_date.isoformat(),
        "end_date": series.end_date,
        "end_date_iso": series.end_date.isoformat(),
        "grouping": series.grouping.value.capitalize(),
        "observation_granularity": series.observation_granularity.value.capitalize(),
        "stale": result.stale,
        "points": points,
        "point_count": len(points),
        "selected_point": (
            {
                "date_label": date_format(selected_point.observation_date, "j M Y"),
                "rate": _rate_text(selected_point.rate),
            }
            if selected_point is not None
            else None
        ),
        "last_point": (
            {
                "date_label": date_format(last.observation_date, "j M Y"),
                "rate": _rate_text(last.rate),
            }
            if last is not None
            else None
        ),
        "minimum": (
            {
                "date_label": date_format(minimum.observation_date, "j M Y"),
                "rate": _rate_text(minimum.rate),
            }
            if minimum is not None
            else None
        ),
        "maximum": (
            {
                "date_label": date_format(maximum.observation_date, "j M Y"),
                "rate": _rate_text(maximum.rate),
            }
            if maximum is not None
            else None
        ),
        "providers": ", ".join(provider_keys) or "Provider attribution unavailable",
        "summary": summary,
        "custom_url": _series_url(
            base=series.base_currency,
            quote=series.quote_currency,
            selected_date=selected_date,
            requested_date=requested_date,
            period="custom",
            start_date=series.start_date,
            end_date=series.end_date,
        ),
    }
