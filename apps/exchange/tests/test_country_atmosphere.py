from __future__ import annotations

from datetime import date

import pytest

from apps.countries.models import Country, CountryCurrency, Currency
from apps.exchange.forms import CurrentConversionForm
from apps.exchange.presentation import build_converter_context


@pytest.mark.django_db
def test_non_featured_country_receives_stable_atmosphere_without_changing_controls():
    united_states = Country.objects.create(iso2="US", iso3="USA", name="United States")
    usd = Currency.objects.create(code="USD", name="US dollar", symbol="$")
    CountryCurrency.objects.create(
        country=united_states,
        currency=usd,
        is_primary=True,
        valid_from=date(1792, 1, 1),
        source="https://example.org/usd",
    )

    form = CurrentConversionForm(
        initial={
            "amount": "10.00",
            "source_country": "US",
            "source_currency": "USD",
            "destination_country": "US",
            "destination_currency": "USD",
        }
    )
    context = build_converter_context(form)

    assert context["source"]["theme"].startswith("atlas-")
    assert context["destination"]["theme"] == context["source"]["theme"]
    assert form.fields["source_currency"].widget.attrs["class"] == "qa-native-select"
