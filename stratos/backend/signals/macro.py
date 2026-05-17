from datetime import UTC, datetime

import polars as pl

from stratos.config import load_config
from stratos.database.db import connect, upsert_job
from stratos.paths import ANALYTICS_PARQUET


def _direction(latest: dict) -> str:
    if latest.get("trend_status") == "bullish" or (latest.get("momentum") or 0) > 0.02:
        return "rising"
    if latest.get("trend_status") == "bearish" or (latest.get("momentum") or 0) < -0.02:
        return "falling"
    return "flat"


def derive_macro_conditions() -> dict[str, str]:
    latest = pl.read_parquet(ANALYTICS_PARQUET).sort("date").group_by("asset").tail(1)
    rows = {row["asset"]: row for row in latest.to_dicts()}
    vix = rows.get("VIX", {})
    equities = rows.get("S&P 500", {})
    return {
        "dxy": _direction(rows.get("DXY", {})),
        "yields": _direction(rows.get("10Y Treasury", {})),
        "vix": "elevated" if (vix.get("close") or 0) >= 25 else "calm" if (vix.get("close") or 0) < 18 else "normal",
        "oil": _direction(rows.get("Oil", {})),
        "btc": _direction(rows.get("Bitcoin", {})),
        "equities": _direction(equities),
    }


def score_regime(conditions: dict[str, str]) -> tuple[str, float, str]:
    cfg = load_config("signals.yaml")["regime"]
    score = 0.0
    score += cfg["weights"]["dxy"] if conditions["dxy"] == "rising" else abs(cfg["weights"]["dxy"]) / 2
    score += cfg["weights"]["yields"] if conditions["yields"] == "rising" else abs(cfg["weights"]["yields"]) / 2
    score += cfg["weights"]["vix"] if conditions["vix"] == "elevated" else abs(cfg["weights"]["vix"]) / 2
    score += cfg["weights"]["oil"] if conditions["oil"] == "rising" else 0
    score += cfg["weights"]["btc"] if conditions["btc"] == "rising" else -10
    score += cfg["weights"]["equities"] if conditions["equities"] == "rising" else -20
    if score >= cfg["risk_on_threshold"]:
        return "Risk-On", score, "Liquidity and cross-asset momentum support selective risk-taking."
    if score <= cfg["risk_off_threshold"]:
        return "Risk-Off", score, "Macro pressure argues for defense, cash discipline, and hedges."
    return "Mixed", score, "Signals are split; favor balanced allocation and position sizing."


def run_macro_signal_job() -> None:
    now = datetime.now(UTC).isoformat()
    conditions = derive_macro_conditions()
    regime, score, summary = score_regime(conditions)
    risks = ", ".join(k for k, v in conditions.items() if v in {"rising", "elevated"} and k in {"dxy", "yields", "vix"})
    opportunities = "strong momentum assets, leading sectors" if regime != "Risk-Off" else "gold, cash, low-volatility exposures"
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO macro_regime(id, as_of, regime, score, summary, key_risks, opportunities)
            VALUES(1, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET as_of=excluded.as_of, regime=excluded.regime,
            score=excluded.score, summary=excluded.summary, key_risks=excluded.key_risks,
            opportunities=excluded.opportunities
            """,
            (now, regime, score, summary, risks or "No dominant macro stress", opportunities),
        )
    upsert_job("macro_signals", "success", now, f"{regime} score {score:.1f}")
