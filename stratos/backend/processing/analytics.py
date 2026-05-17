from datetime import UTC, datetime

import polars as pl

from stratos.config import load_config
from stratos.database.db import upsert_job
from stratos.paths import ANALYTICS_PARQUET, MARKET_PARQUET


def _asset_metrics(frame: pl.DataFrame, windows: dict) -> pl.DataFrame:
    return (
        frame.sort(["asset", "date"])
        .with_columns(pl.col("close").pct_change().over("asset").alias("return_1d"))
        .with_columns([
            (pl.col("close") / pl.col("close").shift(windows["momentum_window"]).over("asset") - 1).alias("momentum"),
            pl.col("close").rolling_mean(windows["short_window"]).over("asset").alias("ma_short"),
            pl.col("close").rolling_mean(windows["long_window"]).over("asset").alias("ma_long"),
            pl.col("close").rolling_max(windows["drawdown_window"]).over("asset").alias("rolling_high"),
            pl.col("return_1d").rolling_std(windows["volatility_window"]).over("asset").alias("volatility_daily"),
        ])
        .with_columns([
            ((pl.col("close") / pl.col("rolling_high")) - 1).alias("drawdown"),
            (pl.col("volatility_daily") * (252 ** 0.5)).alias("volatility"),
            pl.when(pl.col("ma_short") > pl.col("ma_long")).then(pl.lit("bullish"))
            .when(pl.col("ma_short") < pl.col("ma_long")).then(pl.lit("bearish"))
            .otherwise(pl.lit("neutral")).alias("trend_status"),
        ])
    )


def build_analytics() -> pl.DataFrame:
    params = load_config("signals.yaml")["trend"]
    market = pl.read_parquet(MARKET_PARQUET)
    analytics = _asset_metrics(market, params)
    spy = analytics.filter(pl.col("asset") == "SPY").select("date", pl.col("momentum").alias("benchmark_momentum"))
    if spy.is_empty():
        spy = analytics.filter(pl.col("asset") == "S&P 500").select("date", pl.col("momentum").alias("benchmark_momentum"))
    return analytics.join(spy, on="date", how="left").with_columns(
        (pl.col("momentum") - pl.col("benchmark_momentum").fill_null(0)).alias("relative_strength")
    )


def run_analytics_job() -> None:
    now = datetime.now(UTC).isoformat()
    df = build_analytics()
    df.write_parquet(ANALYTICS_PARQUET)
    upsert_job("analytics", "success", now, f"{df.height} analytics rows written")
