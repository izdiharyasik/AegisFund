import plotly.express as px
import streamlit as st


def line_chart(df, x: str, y: str, title: str = "") -> None:
    fig = px.line(df, x=x, y=y, title=title, template="plotly_dark")
    fig.update_layout(margin=dict(l=10, r=10, t=35, b=10), height=280)
    st.plotly_chart(fig, use_container_width=True)


def bar_chart(df, x: str, y: str, title: str = "") -> None:
    fig = px.bar(df, x=x, y=y, title=title, template="plotly_dark")
    fig.update_layout(margin=dict(l=10, r=10, t=35, b=10), height=320)
    st.plotly_chart(fig, use_container_width=True)
