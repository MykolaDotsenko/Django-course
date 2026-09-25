from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from django.db.models import Q

from apps.countries.models import CountryCurrency, Currency


@dataclass(frozen=True, slots=True)
class CurrencySearchOption:
    country_code: str
    country_name: str
    currency_code: str
    currency_name: str
    country_context: bool
    primary: bool
    historical: bool


def _text_rank(value: str, query: str) -> int:
    normalized = value.casefold()
    if normalized == query:
        return 0
    if normalized.startswith(query):
        return 1
    if query in normalized:
        return 2
    return 3


def _option_rank(
    option: CurrencySearchOption,
    *,
    query: str,
    preferred_country_code: str,
    preferred_currency_code: str,
) -> tuple[int, int, str, str]:
    if query:
        if (
            not option.country_context
            and option.currency_code.casefold() == query
            or option.country_context
            and (option.country_code.casefold() == query or option.country_name.casefold() == query)
        ):
            match_rank = 0
        else:
            match_rank = (
                min(
                    _text_rank(option.currency_code, query),
                    _text_rank(option.currency_name, query),
                    _text_rank(option.country_code, query) if option.country_context else 3,
                    _text_rank(option.country_name, query) if option.country_context else 3,
                )
                + 1
            )
        context_rank = 1 if option.country_context else 0
        return (
            match_rank,
            context_rank,
            option.country_name.casefold(),
            option.currency_code,
        )

    preferred_pair = (
        option.country_context
        and option.country_code == preferred_country_code
        and option.currency_code == preferred_currency_code
    )
    preferred_currency = (
        not option.country_context and option.currency_code == preferred_currency_code
    )
    if preferred_pair:
        relevance_rank = 0
    elif preferred_currency:
        relevance_rank = 1
    elif option.country_context and option.primary:
        relevance_rank = 2
    elif option.country_context:
        relevance_rank = 3
    else:
        relevance_rank = 4

    return (
        relevance_rank,
        1 if option.historical else 0,
        option.country_name.casefold(),
        option.currency_code,
    )


def search_currency_options(
    *,
    query: str,
    historical_mode: bool,
    selected_date: date | None = None,
    preferred_country_code: str = "",
    preferred_currency_code: str = "",
    limit: int = 20,
) -> tuple[CurrencySearchOption, ...]:
    """Search local country/currency reference data for the web picker.

    The query is deliberately request-independent and never reaches an external provider.
    """

    if limit <= 0:
        return ()

    normalized_query = " ".join(query.split())[:80]
    query_key = normalized_query.casefold()
    preferred_country = preferred_country_code.upper().strip()
    preferred_currency = preferred_currency_code.upper().strip()

    currency_qs = (
        Currency.objects.all() if historical_mode else Currency.objects.filter(is_active=True)
    )
    if historical_mode and selected_date is not None:
        link_qs = CountryCurrency.objects.on_date(selected_date)
    elif historical_mode:
        link_qs = CountryCurrency.objects.all()
    else:
        link_qs = CountryCurrency.objects.current()

    if normalized_query:
        currency_qs = currency_qs.filter(
            Q(code__icontains=normalized_query) | Q(name__icontains=normalized_query)
        )
        link_qs = link_qs.filter(
            Q(country__iso2__icontains=normalized_query)
            | Q(country__name__icontains=normalized_query)
            | Q(currency__code__icontains=normalized_query)
            | Q(currency__name__icontains=normalized_query)
        )

    currency_rows = currency_qs.only("code", "name", "is_active").order_by("code")
    link_rows = (
        link_qs.select_related("country", "currency")
        .only(
            "country__iso2",
            "country__name",
            "currency__code",
            "currency__name",
            "currency__is_active",
            "is_primary",
            "valid_to",
        )
        .order_by("country__name", "-is_primary", "currency__code")
    )

    candidates: list[CurrencySearchOption] = [
        CurrencySearchOption(
            country_code="",
            country_name="",
            currency_code=currency.code,
            currency_name=currency.name,
            country_context=False,
            primary=False,
            historical=not currency.is_active,
        )
        for currency in currency_rows
    ]

    seen_pairs: set[tuple[str, str]] = set()
    for link in link_rows:
        identity = (link.country.iso2, link.currency.code)
        if identity in seen_pairs:
            continue
        seen_pairs.add(identity)
        candidates.append(
            CurrencySearchOption(
                country_code=link.country.iso2,
                country_name=link.country.name,
                currency_code=link.currency.code,
                currency_name=link.currency.name,
                country_context=True,
                primary=link.is_primary,
                historical=historical_mode
                and (not link.currency.is_active or link.valid_to is not None),
            )
        )

    candidates.sort(
        key=lambda option: _option_rank(
            option,
            query=query_key,
            preferred_country_code=preferred_country,
            preferred_currency_code=preferred_currency,
        )
    )
    return tuple(candidates[:limit])
