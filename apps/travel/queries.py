from __future__ import annotations

from apps.travel.models import FavouritePair


def is_user_favourite(
    user,
    *,
    source_currency: str,
    destination_currency: str,
    source_country: str = "",
    destination_country: str = "",
) -> bool:
    if not user.is_authenticated:
        return False

    favourites = FavouritePair.objects.filter(
        user=user,
        source_currency__code=source_currency.upper(),
        destination_currency__code=destination_currency.upper(),
    )
    if source_country:
        favourites = favourites.filter(source_country__iso2=source_country.upper())
    else:
        favourites = favourites.filter(source_country__isnull=True)
    if destination_country:
        favourites = favourites.filter(destination_country__iso2=destination_country.upper())
    else:
        favourites = favourites.filter(destination_country__isnull=True)
    return favourites.exists()
