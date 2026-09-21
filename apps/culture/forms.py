from __future__ import annotations

from django import forms

from apps.countries.models import Country, Currency
from apps.culture.story import StoryRequest


class StoryRequestForm(forms.Form):
    source_country = forms.CharField(required=False, max_length=2)
    source_currency = forms.CharField(required=False, max_length=3)
    destination_country = forms.CharField(required=False, max_length=2)
    destination_currency = forms.CharField(required=False, max_length=3)
    selected_date = forms.DateField()
    historical = forms.BooleanField(required=False)

    def clean(self):
        cleaned = super().clean()
        if self.errors:
            return cleaned

        for field_name in ("source_country", "destination_country"):
            code = str(cleaned.get(field_name) or "").upper()
            cleaned[field_name] = code
            if code and not Country.objects.filter(iso2=code).exists():
                self.add_error(field_name, "Unknown country code.")

        for field_name in ("source_currency", "destination_currency"):
            code = str(cleaned.get(field_name) or "").upper()
            cleaned[field_name] = code
            if code and not Currency.objects.filter(code=code).exists():
                self.add_error(field_name, "Unknown currency code.")

        if not any(
            cleaned.get(field)
            for field in (
                "source_country",
                "source_currency",
                "destination_country",
                "destination_currency",
            )
        ):
            raise forms.ValidationError("Story context requires a country or currency.")

        return cleaned

    def to_story_request(self) -> StoryRequest:
        if not self.is_valid():
            raise ValueError("StoryRequestForm must be valid before conversion.")
        return StoryRequest(
            source_country=self.cleaned_data["source_country"],
            source_currency=self.cleaned_data["source_currency"],
            destination_country=self.cleaned_data["destination_country"],
            destination_currency=self.cleaned_data["destination_currency"],
            selected_date=self.cleaned_data["selected_date"],
            historical=bool(self.cleaned_data["historical"]),
        )
