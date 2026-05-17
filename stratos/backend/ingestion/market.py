from datetime import UTC, datetime

import polars as pl
import yfinance as yf

from stratos.config import load_config
from stratos.database.db import upsert_job
from stratos.logging_config import get_logger
from stratos.paths import MARKET_PARQUET

LOGGER = get_logger(__name__)


def configured_tickers(groups: tuple[str, ...] = ("market", "sectors", "indonesia", "watchlist")) -> dict[str, str]:
    cfg = load_config("assets.yaml")
    tickers: dict[str, str] = {}
    for group in groups:
        values = cfg.get(group, {})
        if isinstance(values, dict):
            tickers.update({label: symbol for label, symbol in values.items()})
        elif isinstance(values, list):
            tickers.update({symbol: symbol for symbol in values})
    return tickers


def fetch_market_history(period: str = "1y", interval: str = "1d") -> pl.DataFrame:
    rows = []
    for label, symbol in configured_tickers().items():
        data = yf.download(symbol, period=period, interval=interval, progress=False, auto_adjust=True)
        if data.empty:
            LOGGER.warning("No market data returned for %s", symbol)
            continue
        data = data.reset_index()
        date_col = "Datetime" if "Datetime" in data.columns else "Date"
        for record in data.to_dict("records"):
            rows.append({
                "date": str(record[date_col])[:10],
                "asset": label,
                "symbol": symbol,
                "open": float(record.get("Open", 0) or 0),
                "high": float(record.get("High", 0) or 0),
                "low": float(record.get("Low", 0) or 0),
                "close": float(record.get("Close", 0) or 0),
                "volume": float(record.get("Volume", 0) or 0),
            })
    return pl.DataFrame(rows)


def run_market_ingestion() -> None:
    now = datetime.now(UTC).isoformat()
    try:
        df = fetch_market_history()
        if df.is_empty():
            raise RuntimeError("Market ingestion produced no rows")
        df.write_parquet(MARKET_PARQUET)
        upsert_job("market_data", "success", now, f"{df.height} rows written")
    except Exception as exc:
        LOGGER.exception("Market ingestion failed")
        upsert_job("market_data", "failed", now, str(exc))
        raise
