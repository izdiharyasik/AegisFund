from datetime import UTC, datetime, timedelta
import math
import random

import polars as pl

from stratos.database.db import connect, init_db, upsert_job
from stratos.config import load_config
from stratos.backend.processing.analytics import run_analytics_job
from stratos.backend.signals.macro import run_macro_signal_job
from stratos.backend.signals.assets import run_asset_signal_job
from stratos.backend.narrative.engine import run_narrative_job
from stratos.backend.portfolio.analytics import run_portfolio_job
from stratos.paths import MARKET_PARQUET

ASSETS = {
    "DXY": (103, 0.02), "VIX": (17, -0.01), "Oil": (78, 0.04), "Gold": (2350, 0.05),
    "Bitcoin": (65000, 0.12), "S&P 500": (5200, 0.08), "Nasdaq 100": (18000, 0.11),
    "Nikkei 225": (39000, 0.06), "FTSE 100": (8200, 0.03), "USDIDR": (16000, 0.01),
    "JKSE": (7200, 0.04), "10Y Treasury": (43, -0.02), "2Y Treasury": (52, -0.01),
    "XLB": (90, 0.04), "XLE": (95, 0.09), "XLF": (42, 0.06), "XLI": (120, 0.07),
    "XLK": (210, 0.13), "XLP": (78, 0.02), "XLU": (70, 0.01), "XLV": (145, 0.03),
    "XLY": (185, 0.05), "XLRE": (39, -0.01), "XLC": (82, 0.08), "SPY": (520, 0.08),
    "QQQ": (450, 0.11), "GLD": (218, 0.05), "TLT": (92, -0.02), "BTC-USD": (65000, 0.12),
    "ETH-USD": (3100, 0.10), "BBCA.JK": (9500, 0.04), "BBRI.JK": (5000, 0.02), "BMRI.JK": (6400, 0.05),
    "TLKM.JK": (3100, -0.01), "ASII.JK": (5200, 0.01), "ANTM.JK": (1700, 0.07), "ADRO.JK": (2900, 0.08),
}


def create_demo_market_data(days: int = 260) -> None:
    random.seed(42)
    today = datetime.now(UTC).date()
    rows = []
    for asset, (base, trend) in ASSETS.items():
        symbol = asset
        for idx in range(days):
            date = today - timedelta(days=days - idx)
            cycle = math.sin(idx / 19) * 0.015
            noise = random.uniform(-0.01, 0.01)
            close = base * (1 + trend * idx / days + cycle + noise)
            rows.append({
                "date": str(date), "asset": asset, "symbol": symbol, "open": close * 0.995,
                "high": close * 1.01, "low": close * 0.99, "close": close, "volume": random.randint(500000, 5000000),
            })
    pl.DataFrame(rows).write_parquet(MARKET_PARQUET)
    upsert_job("demo_market_data", "success", datetime.now(UTC).isoformat(), f"{len(rows)} rows written")


def seed_watchlist() -> None:
    assets = load_config("assets.yaml").get("watchlist", [])
    with connect() as conn:
        for symbol in assets:
            conn.execute(
                "INSERT OR IGNORE INTO watchlist_assets(symbol, label, group_name, active) VALUES(?, ?, ?, 1)",
                (symbol, symbol, "default"),
            )


def bootstrap_demo() -> None:
    init_db()
    seed_watchlist()
    create_demo_market_data()
    run_analytics_job()
    run_macro_signal_job()
    run_asset_signal_job()
    run_narrative_job()
    run_portfolio_job()


if __name__ == "__main__":
    bootstrap_demo()
