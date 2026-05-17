import streamlit as st

from stratos.frontend.components.style import apply_theme
from stratos.frontend.components.tables import signal_table
from stratos.frontend.data import read_query

st.set_page_config(page_title="StratOS · Watchlist", layout="wide")
apply_theme()
st.title("Watchlist Dashboard")

rows = read_query("SELECT * FROM latest_signals ORDER BY conviction_score DESC")
signal_table(rows, ["asset", "conviction_score", "trend_status", "entry", "take_profit", "stop_loss", "volatility", "macro_alignment"])
