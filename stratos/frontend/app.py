import streamlit as st

from stratos.config import load_config
from stratos.frontend.components.cards import insight_card, metric_card, regime_badge
from stratos.frontend.components.charts import bar_chart
from stratos.frontend.components.style import apply_theme
from stratos.frontend.components.tables import signal_table
from stratos.frontend.data import latest_analytics, read_query, read_table

ui = load_config("ui.yaml")
st.set_page_config(page_title=ui["app_name"], page_icon=ui["page_icon"], layout="wide")
apply_theme()

st.title("StratOS")
st.caption("Personal macro and capital allocation operating system")

regime = (read_table("macro_regime") or [{}])[0]
narratives = read_table("narratives")
signals = read_query("SELECT * FROM latest_signals ORDER BY conviction_score DESC LIMIT 10")
sectors = [row for row in signals if str(row["asset"]).startswith("XL")]

with st.sidebar:
    st.header("Data Health")
    jobs = read_table("job_runs")
    if jobs:
        st.dataframe(jobs, use_container_width=True, hide_index=True)
    else:
        st.caption("No backend job runs recorded yet.")

left, mid, right = st.columns([1.1, 1, 1])
with left:
    st.subheader("Current Macro Regime")
    regime_badge(regime.get("regime", "No data"))
    metric_card("Regime Score", f"{regime.get('score', 0):.1f}")
    st.caption(regime.get("summary", "Run the backend bootstrap or scheduler to populate data."))
with mid:
    st.subheader("Key Risks")
    insight_card("Watch", regime.get("key_risks", "No risks computed"), "bad")
with right:
    st.subheader("Top Opportunities")
    insight_card("Flows", regime.get("opportunities", "No opportunities computed"), "good")

st.divider()
col1, col2 = st.columns(2)
with col1:
    st.subheader("What changed today")
    latest = latest_analytics()
    if not latest.is_empty():
        movers = latest.select("asset", "return_1d").sort("return_1d", descending=True).head(8).to_pandas()
        bar_chart(movers, "asset", "return_1d", "Top 1D movers")
with col2:
    st.subheader("Narrative Engine")
    for item in narratives[:4]:
        insight_card(f"{item['rule_name']} · {item['confidence']:.0%}", item["narrative"] + " " + item["implication"])

st.subheader("Strongest Assets")
signal_table(signals, ["asset", "conviction_score", "trend_status", "momentum", "relative_strength", "macro_alignment"])

st.subheader("Strongest Sectors")
signal_table(sectors[:6], ["asset", "conviction_score", "trend_status", "momentum", "relative_strength"])
