import streamlit as st
import polars as pl

from src.charts import margins as charts


def render(df: pl.DataFrame) -> None:
    st.header("Margin Analysis")

    col_l, col_r = st.columns(2)
    with col_l:
        st.plotly_chart(charts.planned_vs_realised_by_distillery(df), use_container_width=True)
    with col_r:
        st.plotly_chart(charts.margin_gap_distribution(df), use_container_width=True)

    st.plotly_chart(charts.margin_vs_age(df), use_container_width=True)

    st.subheader("Margin Underperformers  (gap < −10 pp)")
    under = charts.underperformers_table(df)
    if under.empty:
        st.info("No SKUs with a margin gap below −10 pp in the current selection.")
    else:
        st.dataframe(under, use_container_width=True, hide_index=True)
