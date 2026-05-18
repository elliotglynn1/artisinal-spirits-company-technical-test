import streamlit as st
import polars as pl

from src.charts import pricing as charts


def render(df: pl.DataFrame) -> None:
    st.header("Pricing Performance")

    col_l, col_r = st.columns(2)
    with col_l:
        st.plotly_chart(charts.rrp_vs_realised(df), use_container_width=True)
    with col_r:
        st.plotly_chart(charts.uplift_erosion_by_distillery(df), use_container_width=True)

    st.plotly_chart(charts.realisation_by_collection_market(df), use_container_width=True)

    st.subheader("Largest Price Erosion — Top 10 SKUs")
    st.dataframe(charts.worst_erosion_table(df), use_container_width=True, hide_index=True)
