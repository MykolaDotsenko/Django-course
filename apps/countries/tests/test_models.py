from datetime import date

import pytest
from django.db import IntegrityError, transaction

from apps.countries.models import Country, CountryCurrency, Currency, primary_currency_for

@pytest.fixture
def finland():
    return Country.objects.create(iso2="FI", iso3="FIN", name="Finland")

@pytest.fixture
def eur():
    return Currency.objects.create(code="EUR", name="Euro", symbol="€")

@pytest.mark.django_db
def test_eur_can_map_to_multiple_countries(eur):
    finland = Country.objects.create(iso2="FI", iso3="FIN", name="Finland")
    france = Country.objects.create(iso2="FR", iso3="FRA", name="France")
    CountryCurrency.objects.create(country=finland, currency=eur, source="test")
    CountryCurrency.objects.create(country=france, currency=eur, source="test")

    assert set(eur.country_links.values_list("country__iso2", flat=True)) == {"FI", "FR"}

@pytest.mark.django_db
def test_primary_currency_query_preserves_historical_relationship(finland, eur):
    fim = Currency.objects.create(code="FIM", name="Finnish markka", is_active=False)
    CountryCurrency.objects.create(
        country=finland,
        currency=fim,
        is_primary=True,
        valid_to=date(2001, 12, 31),
        source="test",
    )
    CountryCurrency.objects.create(
        country=finland,
        currency=eur,
        is_primary=True,
        valid_from=date(2002, 1, 1),
        source="test",
    )

    assert primary_currency_for("FI", date(1998, 6, 15)) == fim
    assert primary_currency_for("FI", date(2026, 9, 20)) == eur
    assert primary_currency_for("FI") == eur

@pytest.mark.django_db
def test_only_one_active_primary_currency_is_allowed(finland, eur):
    CountryCurrency.objects.create(country=finland, currency=eur, is_primary=True, source="test")
    usd = Currency.objects.create(code="USD", name="US dollar")

    with pytest.raises(IntegrityError), transaction.atomic():
        CountryCurrency.objects.create(
            country=finland,
            currency=usd,
            is_primary=True,
            source="test",
        )

@pytest.mark.django_db
def test_archived_currency_remains_representable(finland):
    fim = Currency.objects.create(
        code="FIM",
        name="Finnish markka",
        is_active=False,
        active_to=date(2001, 12, 31),
    )
    link = CountryCurrency.objects.create(
        country=finland,
        currency=fim,
        is_primary=True,
        valid_to=date(2001, 12, 31),
        source="test",
    )

    assert CountryCurrency.objects.on_date(date(1998, 1, 1)).get() == link
    assert not CountryCurrency.objects.current().filter(currency=fim).exists()

@pytest.mark.django_db
def test_current_relationship_excludes_future_valid_from(finland, eur):
    CountryCurrency.objects.create(
        country=finland,
        currency=eur,
        is_primary=True,
        valid_from=date(2099, 1, 1),
        source="test",
    )

    assert not CountryCurrency.objects.current(as_of=date(2026, 9, 20)).exists()
    assert CountryCurrency.objects.current(as_of=date(2099, 1, 1)).exists()


@pytest.mark.django_db
def test_currency_covered_on_treats_latest_observation_as_non_terminal():
    eur = Currency.objects.create(
        code="EUR",
        name="Euro",
        coverage_from=date(1999, 1, 4),
        coverage_to=date(2026, 9, 18),
        coverage_to_is_terminal=False,
    )

    assert Currency.objects.covered_on(date(2026, 9, 20)).get() == eur

@pytest.mark.django_db
def test_currency_covered_on_respects_terminal_archived_coverage():
    fim = Currency.objects.create(
        code="FIM",
        name="Finnish markka",
        is_active=False,
        coverage_from=date(1972, 1, 3),
        coverage_to=date(2001, 12, 28),
        coverage_to_is_terminal=True,
    )

    assert Currency.objects.covered_on(date(1998, 6, 15)).get() == fim
    assert not Currency.objects.covered_on(date(2002, 1, 1)).filter(pk=fim.pk).exists()
