from __future__ import annotations

import json
import socket
from dataclasses import dataclass
from datetime import UTC, date, datetime
from http.client import HTTPException
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from apps.exchange.providers.frankfurter import DEFAULT_BASE_URL

MAX_METADATA_RESPONSE_BYTES = 512 * 1024
SOURCE_VERSION = "frankfurter-v2-currencies"


class FrankfurterMetadataError(RuntimeError):
    pass


@dataclass(frozen=True)
class FrankfurterCurrencyCoverageSnapshot:
    code: str
    name: str
    symbol: str
    coverage_from: date | None
    coverage_to: date | None
    coverage_to_is_terminal: bool
    source_version: str
    fetched_at: datetime


def _optional_date(value: Any, *, field_name: str) -> date | None:
    if value in (None, ""):
        return None
    try:
        return date.fromisoformat(str(value))
    except ValueError as exc:
        raise FrankfurterMetadataError(
            f"Frankfurter currency metadata has invalid {field_name}."
        ) from exc


def _parse_currency_rows(payload: Any) -> dict[str, dict[str, Any]]:
    if not isinstance(payload, list):
        raise FrankfurterMetadataError("Frankfurter currency metadata must be an array.")

    rows: dict[str, dict[str, Any]] = {}
    for raw in payload:
        if not isinstance(raw, dict):
            raise FrankfurterMetadataError("Frankfurter currency metadata row must be an object.")
        code = str(raw.get("iso_code") or "").upper().strip()
        name = str(raw.get("name") or "").strip()
        if len(code) != 3 or not code.isascii() or not code.isalpha() or not name:
            raise FrankfurterMetadataError(
                "Frankfurter currency metadata is missing canonical identity."
            )
        if code in rows:
            raise FrankfurterMetadataError(
                f"Frankfurter currency metadata contains duplicate code {code}."
            )
        rows[code] = raw
    return rows


def build_currency_coverage_snapshots(
    active_payload: Any,
    all_payload: Any,
    *,
    fetched_at: datetime,
) -> tuple[FrankfurterCurrencyCoverageSnapshot, ...]:
    active_rows = _parse_currency_rows(active_payload)
    all_rows = _parse_currency_rows(all_payload)
    if not active_rows.keys() <= all_rows.keys():
        raise FrankfurterMetadataError(
            "Frankfurter active currency set is not a subset of scope=all."
        )

    snapshots: list[FrankfurterCurrencyCoverageSnapshot] = []
    for code, raw in sorted(all_rows.items()):
        coverage_from = _optional_date(raw.get("start_date"), field_name="start_date")
        coverage_to = _optional_date(raw.get("end_date"), field_name="end_date")
        if coverage_from and coverage_to and coverage_to < coverage_from:
            raise FrankfurterMetadataError(
                f"Frankfurter currency metadata has reversed coverage for {code}."
            )
        snapshots.append(
            FrankfurterCurrencyCoverageSnapshot(
                code=code,
                name=str(raw["name"]).strip(),
                symbol=str(raw.get("symbol") or "").strip(),
                coverage_from=coverage_from,
                coverage_to=coverage_to,
                coverage_to_is_terminal=code not in active_rows,
                source_version=SOURCE_VERSION,
                fetched_at=fetched_at,
            )
        )
    return tuple(snapshots)


class FrankfurterMetadataClient:
    def __init__(
        self,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout_seconds: float = 10.0,
    ):
        if timeout_seconds <= 0:
            raise ValueError("Frankfurter metadata timeout must be positive.")
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    def fetch_currency_coverage(self) -> tuple[FrankfurterCurrencyCoverageSnapshot, ...]:
        fetched_at = datetime.now(UTC)
        active_payload = self._fetch_json(f"{self.base_url}/currencies")
        all_payload = self._fetch_json(f"{self.base_url}/currencies?scope=all")
        return build_currency_coverage_snapshots(
            active_payload,
            all_payload,
            fetched_at=fetched_at,
        )

    def _fetch_json(self, url: str) -> Any:
        request = Request(
            url,
            headers={
                "Accept": "application/json",
                "User-Agent": "cultural-currency-converter/0.1",
            },
        )
        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                raw = response.read(MAX_METADATA_RESPONSE_BYTES + 1)
        except HTTPError as exc:
            raise FrankfurterMetadataError(
                f"Frankfurter metadata returned HTTP {exc.code}."
            ) from exc
        except (URLError, HTTPException, OSError) as exc:
            raise FrankfurterMetadataError("Frankfurter metadata request failed.") from exc

        if len(raw) > MAX_METADATA_RESPONSE_BYTES:
            raise FrankfurterMetadataError("Frankfurter metadata response exceeded the size limit.")
        try:
            return json.loads(raw)
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise FrankfurterMetadataError("Frankfurter metadata returned malformed JSON.") from exc
