import streamlit as st

from stratos.frontend.components.charts import bar_chart
from stratos.frontend.components.style import apply_theme
from stratos.frontend.components.tables import signal_table
from stratos.frontend.data import read_query

st.set_page_config(page_title="StratOS · Sector Rotation", layout="wide")
apply_theme()
st.title("Sector Rotation Dashboard")

rows = read_query("SELECT * FROM latest_signals WHERE asset LIKE 'XL%' ORDER BY relative_strength DESC")
if rows:
    bar_chart(rows, "asset", "relative_strength", "Relative strength vs benchmark")
signal_table(rows, ["asset", "conviction_score", "trend_status", "momentum", "relative_strength", "volatility", "drawdown"])
