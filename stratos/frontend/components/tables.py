import streamlit as st


def signal_table(rows: list[dict], columns: list[str] | None = None) -> None:
    if not rows:
        st.info("No precomputed data available. Run `python -m stratos.backend.bootstrap` first.")
        return
    st.dataframe(rows, column_order=columns, use_container_width=True, hide_index=True)
