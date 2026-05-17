import sqlite3

import polars as pl
import streamlit as st

from stratos.paths import ANALYTICS_PARQUET, CACHE_DIR, DB_PATH


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@st.cache_data(ttl=60)
def read_table(table: str) -> list[dict]:
    if not DB_PATH.exists():
        return []
    try:
        with _connect() as conn:
            return [dict(row) for row in conn.execute(f"SELECT * FROM {table}").fetchall()]
    except sqlite3.OperationalError:
        return []


@st.cache_data(ttl=60)
def read_query(query: str) -> list[dict]:
    if not DB_PATH.exists():
        return []
    try:
        with _connect() as conn:
            return [dict(row) for row in conn.execute(query).fetchall()]
    except sqlite3.OperationalError:
        return []


@st.cache_data(ttl=60)
def latest_analytics() -> pl.DataFrame:
    if not ANALYTICS_PARQUET.exists():
        return pl.DataFrame()
    return pl.read_parquet(ANALYTICS_PARQUET).sort("date").group_by("asset").tail(1)


@st.cache_data(ttl=60)
def history(asset: str, days: int = 120) -> pl.DataFrame:
    if not ANALYTICS_PARQUET.exists():
        return pl.DataFrame()
    return pl.read_parquet(ANALYTICS_PARQUET).filter(pl.col("asset") == asset).tail(days)


@st.cache_data(ttl=60)
def crypto_snapshot() -> pl.DataFrame:
    path = CACHE_DIR / "crypto_snapshot.parquet"
    return pl.read_parquet(path) if path.exists() else pl.DataFrame()
