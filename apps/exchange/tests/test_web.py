from datetime import UTC, date, datetime
from decimal import Decimal
from unittest.mock import patch

import pytest
from django.urls import reverse

from apps.countries.models import Country, CountryCurrency, Currency
from apps.exchange.domain import DEFAULT_SOURCE_POLICY, RateQuote
from apps.exchange.providers.base import FxProviderUnavailable


class FakeGateway:
    def __init__(self, *, stale=False):
        self.stale = stale
        self.calls = []

    def get(self, base, quote, policy, *, now):
        self.calls.append((base, quote, policy))
        return (
            RateQuote(
                base_currency=base,
                quote_currency=quote,
                rate=Decimal("174.50") if (base, quote) == ("EUR", "JPY") else Decimal("0.0057"),
                requested_date=None,
                effective_date=date(2026, 9, 18),
                fetched_at=datetime(2026, 9, 20, 8, tzinfo=UTC),
                provider_policy=DEFAULT_SOURCE_POLICY,
                provider_keys=("ecb",),
                historical=False,
            ),
            self.stale,
        )


class UnavailableGateway:
    def get(self, *args, **kwargs):
        raise FxProviderUnavailable("down")


@pytest.fixture
def reference_data(db):
    fi = Country.objects.create(iso2="FI", iso3="FIN", name="Finland")
    jp = Country.objects.create(iso2="JP", iso3="JPN", name="Japan")
    eur = Currency.objects.create(code="EUR", name="Euro", symbol="€", minor_units=2)
    jpy = Currency.objects.create(code="JPY", name="Japanese yen", symbol="¥", minor_units=0)
    CountryCurrency.objects.create(
        country=fi,
        currency=eur,
        is_primary=True,
        source="test",
    )
    CountryCurrency.objects.create(
        country=jp,
        currency=jpy,
        is_primary=True,
        source="test",
    )
    return fi, jp, eur, jpy


def payload(**overrides):
    values = {
        "amount": "100.00",
        "source_country": "FI",
        "source_currency": "EUR",
        "destination_country": "JP",
        "destination_currency": "JPY",
    }
    values.update(overrides)
    return values


@pytest.mark.django_db
def test_initial_page_does_not_request_rate(client, reference_data):
    with patch("apps.exchange.views.build_latest_quote_gateway") as factory:
        response = client.get(reverse("converter"))

    assert response.status_code == 200
    assert b"Ready when you are" in response.content
    factory.assert_not_called()


@pytest.mark.django_db
def test_htmx_conversion_returns_fragment_and_pushes_bookmarkable_url(client, reference_data):
    gateway = FakeGateway()
    with patch("apps.exchange.views.build_latest_quote_gateway", return_value=gateway):
        response = client.post(
            reverse("converter"),
            payload(),
            HTTP_HX_REQUEST="true",
        )

    assert response.status_code == 200
    assert b"<html" not in response.content
    assert b"17450" in response.content
    assert b"18 Sep 2026" in response.content
    assert b"Frankfurter" in response.content
    assert response["HX-Push-Url"].startswith("/?convert=1&")
    assert "HX-Request" in response.get("Vary", "")
    assert len(gateway.calls) == 1


@pytest.mark.django_db
def test_full_post_redirects_to_bookmarkable_get(client, reference_data):
    gateway = FakeGateway()
    with patch("apps.exchange.views.build_latest_quote_gateway", return_value=gateway):
        response = client.post(reverse("converter"), payload())

    assert response.status_code == 302
    assert response["Location"].startswith("/?convert=1&")


@pytest.mark.django_db
def test_invalid_amount_never_builds_provider_gateway(client, reference_data):
    with patch("apps.exchange.views.build_latest_quote_gateway") as factory:
        response = client.post(
            reverse("converter"),
            payload(amount="-1"),
            HTTP_HX_REQUEST="true",
        )

    assert response.status_code == 200
    assert b"zero or a positive amount" in response.content
    factory.assert_not_called()


@pytest.mark.django_db
def test_same_currency_uses_exact_one_without_gateway_call(client, reference_data):
    gateway = FakeGateway()
    with patch("apps.exchange.views.build_latest_quote_gateway", return_value=gateway):
        response = client.post(
            reverse("converter"),
            payload(
                destination_country="",
                destination_currency="EUR",
            ),
            HTTP_HX_REQUEST="true",
        )

    assert response.status_code == 200
    assert b"100.00" in response.content
    assert b"Exact same-currency rate" in response.content
    assert gateway.calls == []


@pytest.mark.django_db
def test_stale_result_is_explicitly_labelled(client, reference_data):
    with patch(
        "apps.exchange.views.build_latest_quote_gateway",
        return_value=FakeGateway(stale=True),
    ):
        response = client.post(reverse("converter"), payload(), HTTP_HX_REQUEST="true")

    assert b"Cached reference" in response.content
    assert b"temporarily unavailable" in response.content


@pytest.mark.django_db
def test_provider_unavailable_preserves_form_without_numeric_result(client, reference_data):
    with patch(
        "apps.exchange.views.build_latest_quote_gateway",
        return_value=UnavailableGateway(),
    ):
        response = client.post(reverse("converter"), payload(), HTTP_HX_REQUEST="true")

    assert response.status_code == 200
    assert b"temporarily unavailable" in response.content
    assert b'value="100.00"' in response.content
    assert b"current-conversion-result" not in response.content


@pytest.mark.django_db
def test_swap_before_first_conversion_does_not_request_rate(client, reference_data):
    gateway = FakeGateway()
    with patch("apps.exchange.views.build_latest_quote_gateway", return_value=gateway):
        response = client.post(
            reverse("converter"),
            payload(action="swap", conversion_active="0"),
            HTTP_HX_REQUEST="true",
        )

    assert response.status_code == 200
    assert b"Japan" in response.content
    assert b"Finland" in response.content
    assert b'value="100.00"' in response.content
    assert b"current-conversion-result" not in response.content
    assert gateway.calls == []


@pytest.mark.django_db
def test_swap_after_success_refreshes_the_swapped_pair(client, reference_data):
    gateway = FakeGateway()
    with patch("apps.exchange.views.build_latest_quote_gateway", return_value=gateway):
        response = client.post(
            reverse("converter"),
            payload(action="swap", conversion_active="1"),
            HTTP_HX_REQUEST="true",
        )

    assert response.status_code == 200
    assert b"current-conversion-result" in response.content
    assert gateway.calls[0][0:2] == ("JPY", "EUR")


@pytest.mark.django_db
def test_picker_search_matches_country_currency_name_and_code(client, reference_data):
    response = client.get(reverse("picker_options"), {"side": "destination", "q": "yen"})

    assert response.status_code == 200
    assert b"Japanese yen" in response.content
    assert b'data-currency-code="JPY"' in response.content


@pytest.mark.django_db
def test_invalid_deep_link_currency_is_validation_state_not_500(client, reference_data):
    with patch("apps.exchange.views.build_latest_quote_gateway") as factory:
        response = client.get(
            reverse("converter"),
            {
                "convert": "1",
                **payload(destination_currency="ZZZ"),
            },
        )

    assert response.status_code == 200
    assert b"Select a valid choice" in response.content
    factory.assert_not_called()
