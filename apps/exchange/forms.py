from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation

from django import forms
from django.utils import timezone

from apps.countries.models import Country, CountryCurrency, Currency

MAX_CONVERSION_AMOUNT = Decimal("1000000000")
RATE_MODE_LATEST = "latest"
RATE_MODE_HISTORICAL = "historical"
RATE_MODE_CHOICES = (
    (RATE_MODE_LATEST, "Latest available"),
    (RATE_MODE_HISTORICAL, "Historical date"),
)
_AMOUNT_PATTERN = re.compile(r"^\d+(?:[.,]\d+)?$")


def parse_amount_text(value: str, *, minor_units: int) -> Decimal:
    """Parse a user-facing amount without guessing grouping semantics."""

    text = value.strip()
    if not text:
        raise forms.ValidationError("Enter an amount.")
    if text.startswith("-"):
        raise forms.ValidationError("Enter zero or a positive amount.")
    if not _AMOUNT_PATTERN.fullmatch(text):
        raise forms.ValidationError(
            "Enter an amount such as 1234.56 or 1234,56, without thousands separators."
        )

    separator = "," if "," in text else "." if "." in text else None
    fraction = text.split(separator, 1)[1] if separator else ""
    integer = text.split(separator, 1)[0] if separator else text
    significant_fraction = fraction.rstrip("0")

    if (
        separator
        and len(fraction) == 3
        and len(significant_fraction) == 3
        and len(integer) <= 3
        and minor_units != 3
    ):
        raise forms.ValidationError(
            "This amount is ambiguous. Enter it without thousands separators."
        )
    if len(significant_fraction) > minor_units:
        unit_label = "decimal place" if minor_units == 1 else "decimal places"
        raise forms.ValidationError(f"This currency supports at most {minor_units} {unit_label}.")

    try:
        amount = Decimal(text.replace(",", "."))
    except InvalidOperation as exc:
        raise forms.ValidationError("Enter a valid decimal amount.") from exc

    if amount > MAX_CONVERSION_AMOUNT:
        raise forms.ValidationError("Enter an amount no greater than 1,000,000,000.")
    return amount


class CurrentConversionForm(forms.Form):
    rate_mode = forms.ChoiceField(
        required=False,
        choices=RATE_MODE_CHOICES,
        initial=RATE_MODE_LATEST,
        widget=forms.RadioSelect,
        label="Rate date",
    )
    requested_date = forms.DateField(
        required=False,
        label="Historical date",
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    amount = forms.CharField(max_length=64, label="Amount")
    source_country = forms.ChoiceField(required=False, label="Source country")
    source_currency = forms.ChoiceField(label="Source currency")
    destination_country = forms.ChoiceField(required=False, label="Destination country")
    destination_currency = forms.ChoiceField(label="Destination currency")

    def __init__(self, *args, **kwargs):
        if args and args[0] is not None and "rate_mode" not in args[0]:
            data = args[0].copy()
            data["rate_mode"] = RATE_MODE_LATEST
            args = (data, *args[1:])
        elif kwargs.get("data") is not None and "rate_mode" not in kwargs["data"]:
            data = kwargs["data"].copy()
            data["rate_mode"] = RATE_MODE_LATEST
            kwargs["data"] = data

        super().__init__(*args, **kwargs)

        raw_mode = (
            self.data.get("rate_mode")
            if self.is_bound
            else self.initial.get("rate_mode", RATE_MODE_LATEST)
        )
        historical_mode = raw_mode == RATE_MODE_HISTORICAL
        currency_query = (
            Currency.objects.all()
            if historical_mode
            else Currency.objects.filter(is_active=True)
        )
        currencies = list(currency_query.order_by("code"))
        countries = list(Country.objects.filter(is_active=True).order_by("name"))

        self._currency_by_code = {currency.code: currency for currency in currencies}
        self._country_by_code = {country.iso2: country for country in countries}

        currency_choices = [
            (currency.code, f"{currency.name} · {currency.code}") for currency in currencies
        ]
        country_choices = [("", "No country context")] + [
            (country.iso2, f"{country.name} · {country.iso2}") for country in countries
        ]

        self.fields["source_currency"].choices = currency_choices
        self.fields["destination_currency"].choices = currency_choices
        self.fields["source_country"].choices = country_choices
        self.fields["destination_country"].choices = country_choices

        self.fields["requested_date"].widget.attrs.update(
            {
                "class": "qa-date-input",
                "max": timezone.localdate().isoformat(),
            }
        )

        for field_name in (
            "source_country",
            "source_currency",
            "destination_country",
            "destination_currency",
        ):
            self.fields[field_name].widget.attrs["class"] = "qa-native-select"

    def add_error(self, field, error):
        super().add_error(field, error)
        if field and field in self.fields and field != "amount":
            self.fields[field].widget.attrs.update(
                {
                    "aria-invalid": "true",
                    "aria-describedby": f"{field}-error",
                }
            )

    @property
    def reference_data_ready(self) -> bool:
        return bool(self._currency_by_code)

    def currency_for_code(self, code: str | None) -> Currency | None:
        return self._currency_by_code.get((code or "").upper())

    def country_for_code(self, code: str | None) -> Country | None:
        return self._country_by_code.get((code or "").upper())

    def clean(self):
        cleaned = super().clean()

        rate_mode = cleaned.get("rate_mode") or RATE_MODE_LATEST
        cleaned["rate_mode"] = rate_mode
        requested_date = cleaned.get("requested_date")
        if rate_mode == RATE_MODE_HISTORICAL:
            if requested_date is None:
                self.add_error("requested_date", "Choose a historical date.")
            elif requested_date > timezone.localdate():
                self.add_error("requested_date", "Historical date cannot be in the future.")
        else:
            cleaned["requested_date"] = None

        source_code = cleaned.get("source_currency")
        source_currency = self.currency_for_code(source_code)
        raw_amount = cleaned.get("amount")
        if source_currency is not None and raw_amount is not None:
            try:
                cleaned["amount_decimal"] = parse_amount_text(
                    raw_amount,
                    minor_units=source_currency.minor_units,
                )
            except forms.ValidationError as exc:
                self.add_error("amount", exc)

        if rate_mode == RATE_MODE_LATEST:
            self._validate_country_currency("source", cleaned)
            self._validate_country_currency("destination", cleaned)
        return cleaned

    @property
    def historical_mode(self) -> bool:
        if self.is_bound:
            return self.data.get("rate_mode") == RATE_MODE_HISTORICAL
        return self.initial.get("rate_mode") == RATE_MODE_HISTORICAL

    def _validate_country_currency(self, side: str, cleaned: dict[str, object]) -> None:
        country_code = cleaned.get(f"{side}_country")
        currency_code = cleaned.get(f"{side}_currency")
        if not country_code or not currency_code:
            return

        exists = (
            CountryCurrency.objects.current()
            .filter(
                country__iso2=country_code,
                currency__code=currency_code,
            )
            .exists()
        )
        if not exists:
            self.add_error(
                f"{side}_currency",
                "Choose a currency currently associated with this country, "
                "or remove the country context.",
            )
