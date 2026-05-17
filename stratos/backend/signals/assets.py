from datetime import UTC, datetime

import polars as pl

from stratos.config import load_config
from stratos.database.db import connect, upsert_job
from stratos.paths import ANALYTICS_PARQUET


def _conviction(row: dict, macro_regime: str, weights: dict) -> float:
    momentum = max(min((row.get("momentum") or 0) * 250, 100), 0)
    trend = 100 if row.get("trend_status") == "bullish" else 35 if row.get("trend_status") == "neutral" else 0
    rs = max(min(((row.get("relative_strength") or 0) + 0.10) * 500, 100), 0)
    macro = 85 if macro_regime == "Risk-On" and trend > 50 else 45 if macro_regime == "Mixed" else 25
    return round(momentum * weights["momentum"] + trend * weights["trend"] + rs * weights["relative_strength"] + macro * weights["macro_alignment"], 1)


def run_asset_signal_job() -> None:
    now = datetime.now(UTC).isoformat()
    cfg = load_config("signals.yaml")["watchlist"]
    latest = pl.read_parquet(ANALYTICS_PARQUET).sort("date").group_by("asset").tail(1).to_dicts()
    with connect() as conn:
        regime = conn.execute("SELECT regime FROM macro_regime WHERE id = 1").fetchone()
        macro_regime = regime["regime"] if regime else "Mixed"
        for row in latest:
            close = row.get("close") or 0
            vol = row.get("volatility") or 0
            atr_proxy = close * max(vol, 0.01) / (252 ** 0.5)
            conviction = _conviction(row, macro_regime, cfg["conviction_weights"])
            conn.execute(
                """
                INSERT INTO latest_signals VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(asset) DO UPDATE SET as_of=excluded.as_of, momentum=excluded.momentum,
                relative_strength=excluded.relative_strength, trend_status=excluded.trend_status,
                volatility=excluded.volatility, drawdown=excluded.drawdown, macro_alignment=excluded.macro_alignment,
                conviction_score=excluded.conviction_score, entry=excluded.entry,
                take_profit=excluded.take_profit, stop_loss=excluded.stop_loss
                """,
                (row["asset"], "market", now, row.get("momentum"), row.get("relative_strength"), row.get("trend_status"),
                 row.get("volatility"), row.get("drawdown"), macro_regime, conviction, close * (1 + cfg["entry_buffer"]),
                 close + cfg["take_profit_atr"] * atr_proxy, close - cfg["stop_loss_atr"] * atr_proxy),
            )
    upsert_job("asset_signals", "success", now, f"{len(latest)} signals written")
