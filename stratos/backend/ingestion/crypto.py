from datetime import UTC, datetime

import polars as pl
import requests

from stratos.config import load_config
from stratos.database.db import upsert_job
from stratos.logging_config import get_logger
from stratos.paths import CACHE_DIR

LOGGER = get_logger(__name__)
COINGECKO_URL = "https://api.coingecko.com/api/v3/coins/markets"


def run_crypto_ingestion() -> None:
    now = datetime.now(UTC).isoformat()
    ids = ",".join(load_config("assets.yaml").get("crypto", {}).keys())
    try:
        response = requests.get(
            COINGECKO_URL,
            params={"vs_currency": "usd", "ids": ids, "price_change_percentage": "24h,7d,30d"},
            timeout=20,
        )
        response.raise_for_status()
        df = pl.DataFrame(response.json()).with_columns(pl.lit(now).alias("as_of"))
        df.write_parquet(CACHE_DIR / "crypto_snapshot.parquet")
        upsert_job("crypto", "success", now, f"{df.height} assets written")
    except Exception as exc:
        LOGGER.exception("Crypto ingestion failed")
        upsert_job("crypto", "failed", now, str(exc))
        raise
