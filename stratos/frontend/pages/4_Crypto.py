import streamlit as st

from stratos.frontend.components.charts import line_chart
from stratos.frontend.components.style import apply_theme
from stratos.frontend.components.tables import signal_table
from stratos.frontend.data import crypto_snapshot, history, read_query

st.set_page_config(page_title="StratOS · Crypto", layout="wide")
apply_theme()
st.title("Crypto Dashboard")

cols = st.columns(2)
for idx, asset in enumerate(["Bitcoin", "BTC-USD", "ETH-USD"]):
    with cols[idx % 2]:
        df = history(asset).to_pandas()
        if not df.empty:
            line_chart(df, "date", "close", asset)

snapshot = crypto_snapshot()
if not snapshot.is_empty():
    st.subheader("CoinGecko Snapshot")
    st.dataframe(snapshot.to_pandas(), use_container_width=True)

rows = read_query("SELECT * FROM latest_signals WHERE asset IN ('Bitcoin','BTC-USD','ETH-USD') ORDER BY conviction_score DESC")
signal_table(rows, ["asset", "conviction_score", "trend_status", "momentum", "relative_strength", "volatility"])
