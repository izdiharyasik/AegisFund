import streamlit as st

from stratos.frontend.components.charts import line_chart
from stratos.frontend.components.style import apply_theme
from stratos.frontend.components.tables import signal_table
from stratos.frontend.data import history, read_query

st.set_page_config(page_title="StratOS · Global Macro", layout="wide")
apply_theme()
st.title("Global Macro Dashboard")

assets = ["DXY", "10Y Treasury", "VIX", "Oil", "Gold", "Bitcoin", "S&P 500", "Nasdaq 100"]
cols = st.columns(2)
for idx, asset in enumerate(assets):
    with cols[idx % 2]:
        df = history(asset).to_pandas()
        if not df.empty:
            line_chart(df, "date", "close", asset)

st.subheader("Macro Signals")
rows = read_query("SELECT * FROM latest_signals WHERE asset IN ('DXY','10Y Treasury','VIX','Oil','Gold','Bitcoin','S&P 500')")
signal_table(rows, ["asset", "trend_status", "momentum", "volatility", "drawdown", "conviction_score"])
