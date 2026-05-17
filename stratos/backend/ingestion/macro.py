import os
from datetime import UTC, datetime, timedelta

import polars as pl
from fredapi import Fred

from stratos.database.db import upsert_job
from stratos.logging_config import get_logger
from stratos.paths import CACHE_DIR

LOGGER = get_logger(__name__)
SERIES = {"FEDFUNDS": "fed_funds", "CPIAUCSL": "cpi", "UNRATE": "unemployment"}


def run_macro_ingestion() -> None:
    now = datetime.now(UTC).isoformat()
    api_key = os.getenv("FRED_API_KEY")
    if not api_key:
        upsert_job("macro_fred", "failed", now, "FRED_API_KEY is not configured")
        return
    try:
        fred = Fred(api_key=api_key)
        rows = []
        start = (datetime.now(UTC) - timedelta(days=365 * 5)).date()
        for series_id, label in SERIES.items():
            data = fred.get_series(series_id, observation_start=start)
            for date, value in data.dropna().items():
                rows.append({"date": str(date.date()), "series": label, "value": float(value)})
        pl.DataFrame(rows).write_parquet(CACHE_DIR / "macro_fred.parquet")
        upsert_job("macro_fred", "success", now, f"{len(rows)} rows written")
    except Exception as exc:
        LOGGER.exception("Macro ingestion failed")
        upsert_job("macro_fred", "failed", now, str(exc))
        raise
