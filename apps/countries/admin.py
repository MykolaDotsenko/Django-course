from django.contrib import admin

from apps.countries.models import Country, CountryCurrency, Currency


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ("iso2", "name", "region", "is_active", "metadata_source")
    list_filter = ("is_active", "region")
    search_fields = ("iso2", "iso3", "name", "official_name")


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "minor_units", "is_active", "active_from", "active_to")
    list_filter = ("is_active",)
    search_fields = ("code", "name")


@admin.register(CountryCurrency)
class CountryCurrencyAdmin(admin.ModelAdmin):
    list_display = (
        "country",
        "currency",
        "is_primary",
        "valid_from",
        "valid_to",
        "usage_role",
    )
    list_filter = ("is_primary", "usage_role")
    search_fields = ("country__iso2", "country__name", "currency__code", "currency__name")
    list_select_related = ("country", "currency")
