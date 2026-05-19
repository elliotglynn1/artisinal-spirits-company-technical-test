import streamlit as st
import polars as pl

from src.charts import overview as charts
from src.charts import margins as margin_charts
from src.data.models import OverviewMetrics

_DATA_NOTES = """
**Column encoding quirks:**
- `Margin %` columns are stored as whole integers (42 = 42%)
- `Days to Sell Out` is `N/A` for items not yet sold out — treated as null
"""


def render(df: pl.DataFrame) -> None:
    st.header("Portfolio Overview")

    m = OverviewMetrics.from_df(df)

    # ── Demand ───────────────────────────────────────────────────────────────
    st.subheader("Demand")
    c1, c2, c3 = st.columns(3)
    c1.metric("Avg Sell-Through", f"{m.avg_sell_through:.1f}%")
    c2.metric("Total Bottles Sold", f"{m.total_bottles_sold:,}")
    c3.metric("SKUs Fully Sold Out", f"{m.n_sold_out} / {m.n_skus}")

    col_l, col_r = st.columns(2)
    with col_l:
        st.plotly_chart(charts.sell_through_by_distillery(df), use_container_width=True)
    with col_r:
        st.plotly_chart(charts.sell_through_by_collection_market(df), use_container_width=True)

    st.divider()

    # ── Pricing Efficiency ───────────────────────────────────────────────────
    st.subheader("Pricing Efficiency")
    c1, c2 = st.columns(2)
    c1.metric("Avg Price Realisation", f"{m.avg_price_realisation:.1f}%")
    sign = "+" if m.avg_price_uplift >= 0 else ""
    c2.metric("Avg Price Uplift / Erosion", f"£{sign}{m.avg_price_uplift:.2f}",
              delta_color="normal" if m.avg_price_uplift >= 0 else "inverse")

    st.plotly_chart(charts.price_realisation_by_distillery(df), use_container_width=True)

    st.divider()

    # ── Profit ───────────────────────────────────────────────────────────────
    st.subheader("Profit")
    c1, c2, c3 = st.columns(3)
    c1.metric("Avg Planned Margin", f"{m.avg_planned_margin:.1f}%")
    c2.metric("Avg Realised Margin", f"{m.avg_realised_margin:.1f}%")
    c3.metric("Avg Margin Gap", f"{m.avg_margin_gap:+.1f} pp", delta_color="inverse")

    st.plotly_chart(margin_charts.planned_vs_realised_by_distillery(df),
                    use_container_width=True, key="overview_profit_margin")

    st.divider()

    # ── Revenue ──────────────────────────────────────────────────────────────
    st.subheader("Revenue")
    st.metric("Total Revenue", f"£{m.total_revenue:,.0f}")

    col_l, col_r = st.columns(2)
    with col_l:
        st.plotly_chart(charts.revenue_treemap(df), use_container_width=True)
    with col_r:
        st.plotly_chart(charts.revenue_by_market(df), use_container_width=True)

    with st.expander("⚠️ Raw data quality notes"):
        st.markdown(_DATA_NOTES)
