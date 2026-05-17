from datetime import UTC, datetime

import polars as pl

from stratos.config import load_config
from stratos.database.db import connect, upsert_job
from stratos.paths import ANALYTICS_PARQUET

DEFAULT_POSITIONS = [
    ("SPY", "S&P 500 ETF", "equity", 35000.0, 30000.0, 0.35),
    ("QQQ", "Nasdaq 100 ETF", "equity", 25000.0, 21000.0, 0.25),
    ("GLD", "Gold ETF", "commodity", 15000.0, 14000.0, 0.15),
    ("TLT", "Long Treasury ETF", "fixed_income", 10000.0, 10500.0, 0.15),
    ("BTC-USD", "Bitcoin", "crypto", 15000.0, 9000.0, 0.10),
]


def seed_portfolio() -> None:
    with connect() as conn:
        count = conn.execute("SELECT COUNT(*) AS count FROM portfolio_positions").fetchone()["count"]
        if count == 0:
            conn.executemany("INSERT INTO portfolio_positions VALUES(?, ?, ?, ?, ?, ?)", DEFAULT_POSITIONS)


def run_portfolio_job() -> None:
    now = datetime.now(UTC).isoformat()
    cfg = load_config("signals.yaml")["portfolio"]
    seed_portfolio()
    with connect() as conn:
        positions = conn.execute("SELECT * FROM portfolio_positions").fetchall()
        total = sum(row["market_value"] for row in positions) or 1
        max_position = max(row["market_value"] / total for row in positions)
        by_class: dict[str, float] = {}
        for row in positions:
            by_class[row["asset_class"]] = by_class.get(row["asset_class"], 0) + row["market_value"] / total
        concentration_label = "High" if max_position > cfg["concentration_warning"] else "Balanced"
        _write_metric(conn, "total_value", now, total, "$", "Current portfolio market value")
        _write_metric(conn, "max_position_weight", now, max_position, concentration_label, "Largest single-position exposure")
        for asset_class, weight in by_class.items():
            _write_metric(conn, f"exposure_{asset_class}", now, weight, asset_class, "Asset-class exposure")
        _write_correlation_metric(conn, now, cfg)
    upsert_job("portfolio", "success", now, "Portfolio analytics refreshed")


def _write_metric(conn, metric: str, as_of: str, value: float, label: str, detail: str) -> None:
    conn.execute(
        """
        INSERT INTO portfolio_metrics(metric, as_of, value, label, detail) VALUES(?, ?, ?, ?, ?)
        ON CONFLICT(metric) DO UPDATE SET as_of=excluded.as_of, value=excluded.value,
        label=excluded.label, detail=excluded.detail
        """,
        (metric, as_of, float(value), label, detail),
    )


def _write_correlation_metric(conn, as_of: str, cfg: dict) -> None:
    try:
        df = pl.read_parquet(ANALYTICS_PARQUET)
        pivot = df.select("date", "asset", "return_1d").pivot(values="return_1d", index="date", columns="asset")
        corr = pivot.drop("date").corr().fill_nan(0)
        values = [abs(v) for row in corr.to_numpy().tolist() for v in row if abs(v) < 0.999]
        avg_corr = sum(values) / len(values) if values else 0
        label = "Clustered" if avg_corr > cfg["correlation_warning"] else "Diversified"
        _write_metric(conn, "average_correlation", as_of, avg_corr, label, "Average absolute cross-asset correlation")
    except Exception:
        _write_metric(conn, "average_correlation", as_of, 0, "Unavailable", "Correlation requires analytics data")
