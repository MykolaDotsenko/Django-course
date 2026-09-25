from __future__ import annotations

from apps.exchange.cache import HistoricalQuoteGateway, HistoricalSeriesGateway, LatestQuoteGateway
from apps.exchange.config import load_fx_runtime_config


def build_latest_quote_gateway() -> LatestQuoteGateway:
    config = load_fx_runtime_config()
    return LatestQuoteGateway(config.build_provider())


def build_historical_quote_gateway() -> HistoricalQuoteGateway:
    config = load_fx_runtime_config()
    return HistoricalQuoteGateway(config.build_provider())


def build_historical_series_gateway() -> HistoricalSeriesGateway:
    config = load_fx_runtime_config()
    return HistoricalSeriesGateway(config.build_provider())
