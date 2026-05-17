import streamlit as st

from stratos.frontend.components.cards import metric_card
from stratos.frontend.components.style import apply_theme
from stratos.frontend.components.tables import signal_table
from stratos.frontend.data import read_table

st.set_page_config(page_title="StratOS · Portfolio", layout="wide")
apply_theme()
st.title("Portfolio Dashboard")

metrics = {row["metric"]: row for row in read_table("portfolio_metrics")}
cols = st.columns(3)
with cols[0]:
    metric_card("Total Value", f"${metrics.get('total_value', {}).get('value', 0):,.0f}")
with cols[1]:
    metric_card("Max Position", f"{metrics.get('max_position_weight', {}).get('value', 0):.1%}", metrics.get('max_position_weight', {}).get('label'))
with cols[2]:
    metric_card("Average Correlation", f"{metrics.get('average_correlation', {}).get('value', 0):.2f}", metrics.get('average_correlation', {}).get('label'))

st.subheader("Positions")
signal_table(read_table("portfolio_positions"))
st.subheader("Exposure Metrics")
signal_table(list(metrics.values()))
