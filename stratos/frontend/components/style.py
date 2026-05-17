import streamlit as st

from stratos.config import load_config


def apply_theme() -> None:
    colors = load_config("ui.yaml")["colors"]
    st.markdown(
        f"""
        <style>
        .stApp {{ background: {colors['bg']}; color: {colors['text']}; }}
        div[data-testid="stMetric"] {{ background: {colors['surface']}; border: 1px solid {colors['border']};
            padding: 14px; border-radius: 12px; }}
        .stratos-card {{ background: {colors['surface']}; border: 1px solid {colors['border']};
            padding: 14px; border-radius: 12px; margin-bottom: 10px; }}
        .badge {{ padding: 4px 9px; border-radius: 999px; font-size: 0.78rem; font-weight: 700; }}
        .good {{ background: rgba(46,204,113,.18); color: {colors['good']}; }}
        .warn {{ background: rgba(241,196,15,.18); color: {colors['warn']}; }}
        .bad {{ background: rgba(231,76,60,.18); color: {colors['bad']}; }}
        .muted {{ color: {colors['muted']}; font-size: .86rem; }}
        </style>
        """,
        unsafe_allow_html=True,
    )
