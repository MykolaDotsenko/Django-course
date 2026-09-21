from django.core.management import call_command

import pytest

from apps.countries.models import Currency


@pytest.mark.django_db
def test_reference_seed_persists_currency_minor_units():
    call_command("seed_reference_data")

    assert Currency.objects.get(code="EUR").minor_units == 2
    assert Currency.objects.get(code="JPY").minor_units == 0
    assert Currency.objects.get(code="USD").minor_units == 2
    assert Currency.objects.get(code="FIM").minor_units == 2
