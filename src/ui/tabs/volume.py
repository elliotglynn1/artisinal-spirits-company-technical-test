import streamlit as st
import polars as pl

from src.charts import volume as charts


def render(df: pl.DataFrame) -> None:
    st.header("Volume & Revenue Analysis")

    col_l, col_r = st.columns(2)
    with col_l:
        st.plotly_chart(charts.sell_through_by_collection_market(df), use_container_width=True)
    with col_r:
        st.plotly_chart(charts.allocation_vs_sold(df), use_container_width=True)

    st.subheader("Revenue Efficiency Heatmap")
    st.caption("Revenue efficiency = Realised Price × Sell-Through  (higher = better)")
    st.plotly_chart(charts.revenue_efficiency_heatmap(df), use_container_width=True)

    st.subheader("Low Sell-Through SKUs  (< 60%)")
    low = charts.low_sell_through_table(df)
    if low.empty:
        st.info("No SKUs below 60% sell-through in current selection.")
    else:
        st.dataframe(low, use_container_width=True, hide_index=True)
