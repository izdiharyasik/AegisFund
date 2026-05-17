import streamlit as st


def metric_card(label: str, value: str, delta: str | None = None) -> None:
    st.metric(label, value, delta=delta)


def badge(text: str, tone: str = "warn") -> str:
    return f'<span class="badge {tone}">{text}</span>'


def regime_badge(regime: str) -> None:
    tone = "good" if regime == "Risk-On" else "bad" if regime == "Risk-Off" else "warn"
    st.markdown(badge(regime, tone), unsafe_allow_html=True)


def insight_card(title: str, body: str, tone: str = "warn") -> None:
    st.markdown(f'<div class="stratos-card"><b>{title}</b><br><span class="muted">{body}</span></div>', unsafe_allow_html=True)
