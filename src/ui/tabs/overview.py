import streamlit as st
import polars as pl

from src.charts import overview as charts
from src.data.models import OverviewMetrics

_DATA_NOTES = """
**Column encoding quirks:**
- `Margin %` columns are stored as whole integers (42 = 42%)
- `Days to Sell Out` is `N/A` for items not yet sold out — treated as null
"""


def render(df: pl.DataFrame) -> None:
    st.header("Portfolio Overview")

    m = OverviewMetrics.from_df(df)
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("SKUs", m.n_skus)
    c2.metric("Total Revenue", f"£{m.total_revenue:,.0f}")
    c3.metric("Avg Sell-Through", f"{m.avg_sell_through:.1f}%")
    c4.metric("Avg Price Realisation", f"{m.avg_price_realisation:.1f}%")
    c5.metric("Avg Margin Gap", f"{m.avg_margin_gap:+.1f} pp", delta_color="inverse")

    st.divider()
    col_l, col_r = st.columns(2)
    with col_l:
        st.plotly_chart(charts.revenue_by_distillery(df), use_container_width=True)
    with col_r:
        st.plotly_chart(charts.revenue_share_by_collection(df), use_container_width=True)

    st.subheader("Market Comparison")
    st.dataframe(charts.market_comparison(df), use_container_width=True)

    with st.expander("⚠️ Raw data quality notes"):
        st.markdown(_DATA_NOTES)
