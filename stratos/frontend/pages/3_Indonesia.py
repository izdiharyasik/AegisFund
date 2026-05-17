import streamlit as st

from stratos.frontend.components.charts import line_chart
from stratos.frontend.components.style import apply_theme
from stratos.frontend.components.tables import signal_table
from stratos.frontend.data import history, read_query

st.set_page_config(page_title="StratOS · Indonesia", layout="wide")
apply_theme()
st.title("Indonesia Dashboard")

for asset in ["JKSE", "USDIDR"]:
    df = history(asset).to_pandas()
    if not df.empty:
        line_chart(df, "date", "close", asset)

rows = read_query("SELECT * FROM latest_signals WHERE asset IN ('BBCA.JK','BBRI.JK','BMRI.JK','TLKM.JK','ASII.JK','ANTM.JK','ADRO.JK') ORDER BY conviction_score DESC")
st.subheader("IDX and commodity-linked equities")
signal_table(rows, ["asset", "conviction_score", "trend_status", "momentum", "relative_strength", "volatility"])
