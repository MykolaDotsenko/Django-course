from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen

REST_COUNTRIES_V5_BASE_URL = "https://api.restcountries.com/countries/v5"
RESPONSE_FIELDS = (
    "names.common",
    "names.official",
    "codes.alpha_2",
    "codes.alpha_3",
    "capitals",
    "region",
    "subregion",
    "currencies",
    "flag.url_svg",
)


class CountrySourceError(RuntimeError):
    pass


@dataclass(frozen=True)
class CurrencySnapshot:
    code: str
    name: str
    symbol: str = ""
    minor_units: int = 2


@dataclass(frozen=True)
class CountryMetadataSnapshot:
    iso2: str
    iso3: str
    name: str
    official_name: str
    capital: str
    region: str
    subregion: str
    flag_url: str
    currencies: tuple[CurrencySnapshot, ...]
    source_version: str
    fetched_at: datetime


def _first_text(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, list) and value and isinstance(value[0], str):
        return value[0]
    if isinstance(value, dict):
        for key in ("name", "common", "value"):
            candidate = value.get(key)
            if isinstance(candidate, str):
                return candidate
    return ""


def _parse_currencies(value: Any) -> tuple[CurrencySnapshot, ...]:
    items: list[tuple[str, Any]]
    if isinstance(value, dict):
        items = list(value.items())
    elif isinstance(value, list):
        items = [
            (str(item.get("code", "")), item)
            for item in value
            if isinstance(item, dict)
        ]
    else:
        items = []

    currencies: list[CurrencySnapshot] = []
    for raw_code, raw in items:
        if not isinstance(raw, dict):
            continue
        code = str(raw.get("code") or raw_code).upper().strip()
        if len(code) != 3:
            continue
        name = str(raw.get("name") or code).strip()
        symbol = str(raw.get("symbol") or "").strip()
        raw_minor_units = raw.get("minor_units", raw.get("decimal_digits", 2))
        try:
            minor_units = int(raw_minor_units)
        except (TypeError, ValueError):
            minor_units = 2
        if not 0 <= minor_units <= 6:
            minor_units = 2
        currencies.append(CurrencySnapshot(code, name, symbol, minor_units))
    return tuple(sorted(currencies, key=lambda item: item.code))


def parse_country_object(raw: dict[str, Any], *, fetched_at: datetime) -> CountryMetadataSnapshot:
    names = raw.get("names") if isinstance(raw.get("names"), dict) else {}
    codes = raw.get("codes") if isinstance(raw.get("codes"), dict) else {}
    flag = raw.get("flag") if isinstance(raw.get("flag"), dict) else {}

    iso2 = str(codes.get("alpha_2") or raw.get("cca2") or "").upper().strip()
    iso3 = str(codes.get("alpha_3") or raw.get("cca3") or "").upper().strip()
    name = str(names.get("common") or raw.get("name") or "").strip()
    if len(iso2) != 2 or len(iso3) != 3 or not name:
        raise CountrySourceError("REST Countries object is missing canonical country identity")

    return CountryMetadataSnapshot(
        iso2=iso2,
        iso3=iso3,
        name=name,
        official_name=str(names.get("official") or name).strip(),
        capital=_first_text(raw.get("capitals")),
        region=_first_text(raw.get("region")),
        subregion=_first_text(raw.get("subregion")),
        flag_url=str(flag.get("url_svg") or "").strip(),
        currencies=_parse_currencies(raw.get("currencies")),
        source_version="rest-countries-v5",
        fetched_at=fetched_at,
    )


class RestCountriesV5Client:
    def __init__(
        self,
        *,
        api_key: str,
        base_url: str = REST_COUNTRIES_V5_BASE_URL,
        timeout_seconds: float = 10.0,
    ):
        if not api_key:
            raise ValueError("REST Countries API key is required")
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    def fetch_all(self) -> tuple[CountryMetadataSnapshot, ...]:
        fetched_at = datetime.now(UTC)
        offset = 0
        snapshots: list[CountryMetadataSnapshot] = []

        while True:
            query = urlencode(
                {
                    "limit": 100,
                    "offset": offset,
                    "response_fields": ",".join(RESPONSE_FIELDS),
                }
            )
            request = Request(
                f"{self.base_url}?{query}",
                headers={
                    "Accept": "application/json",
                    "Authorization": f"Bearer {self.api_key}",
                    "User-Agent": "cultural-currency-converter/0.1",
                },
            )
            try:
                with urlopen(request, timeout=self.timeout_seconds) as response:
                    if response.status != 200:
                        raise CountrySourceError(
                            f"REST Countries returned HTTP {response.status}"
                        )
                    payload = json.load(response)
            except CountrySourceError:
                raise
            except Exception as exc:
                raise CountrySourceError("REST Countries request failed") from exc

            data = payload.get("data") if isinstance(payload, dict) else None
            objects = data.get("objects") if isinstance(data, dict) else None
            meta = data.get("meta") if isinstance(data, dict) else None
            if not isinstance(objects, list) or not isinstance(meta, dict):
                raise CountrySourceError("REST Countries response shape is invalid")

            snapshots.extend(
                parse_country_object(item, fetched_at=fetched_at)
                for item in objects
                if isinstance(item, dict)
            )
            if not meta.get("more"):
                break
            count = int(meta.get("count") or len(objects))
            if count <= 0:
                raise CountrySourceError("REST Countries pagination made no progress")
            offset += count

        return tuple(snapshots)
