import plotly.express as px
import plotly.graph_objects as go
import polars as pl


# ── Demand ───────────────────────────────────────────────────────────────────

def sell_through_by_distillery(df: pl.DataFrame) -> go.Figure:
    data = (
        df.group_by("Distillery")
        .agg(pl.col("Sell Through (%)").mean().round(1).alias("Avg Sell-Through %"))
        .sort("Avg Sell-Through %")
        .to_pandas()
    )
    fig = px.bar(
        data, x="Avg Sell-Through %", y="Distillery", orientation="h",
        title="Avg Sell-Through % by Distillery",
        color="Avg Sell-Through %",
        color_continuous_scale=["#c4784a", "#f5ede8"],
        range_color=[50, 100],
    )
    fig.add_vline(x=100, line_dash="dash", line_color="rgba(196,120,74,0.5)",
                  annotation_text="Full sell-through")
    fig.update_layout(coloraxis_showscale=False, xaxis_range=[0, 110],
                      yaxis_title="", xaxis_title="Avg Sell-Through %")
    return fig


def sell_through_by_collection_market(df: pl.DataFrame) -> go.Figure:
    data = (
        df.group_by(["Collection Type", "Market"])
        .agg(pl.col("Sell Through (%)").mean().round(1).alias("Avg Sell-Through %"))
        .sort("Avg Sell-Through %", descending=True)
        .to_pandas()
    )
    fig = px.bar(
        data, x="Collection Type", y="Avg Sell-Through %",
        color="Market", barmode="group",
        title="Avg Sell-Through % by Collection & Market",
    )
    fig.add_hline(y=100, line_dash="dash", line_color="rgba(196,120,74,0.5)",
                  annotation_text="Full sell-through")
    return fig


# ── Pricing Efficiency ───────────────────────────────────────────────────────

def price_realisation_by_distillery(df: pl.DataFrame) -> go.Figure:
    data = (
        df.group_by("Distillery")
        .agg([
            pl.col("Pricing Realisation (%)").mean().round(1).alias("Avg Price Realisation %"),
            pl.col("Price uplift / erosision (£)").mean().round(2).alias("Avg Price Uplift (£)"),
        ])
        .sort("Avg Price Realisation %", descending=True)
        .to_pandas()
    )
    fig = px.bar(
        data, x="Distillery", y="Avg Price Realisation %",
        title="Avg Price Realisation % by Distillery",
        hover_data=["Avg Price Uplift (£)"],
        color="Avg Price Realisation %",
        color_continuous_scale=["#c4784a", "#f5ede8"],
    )
    fig.add_hline(y=100, line_dash="dash", line_color="rgba(196,120,74,0.5)",
                  annotation_text="Target RRP")
    fig.update_layout(coloraxis_showscale=False, yaxis_title="Avg Price Realisation %")
    return fig


# ── Profit & Revenue ─────────────────────────────────────────────────────────

def revenue_vs_margin_scatter(df: pl.DataFrame) -> go.Figure:
    data = (
        df.group_by(["Distillery", "Distillery Group"])
        .agg([
            pl.col("Revenue (£)").sum().alias("Revenue (£)"),
            pl.col("Realised Margin %").mean().round(1).alias("Realised Margin %"),
            pl.col("Planned Margin %").mean().round(1).alias("Planned Margin %"),
            pl.col("Bottles Sold").sum().alias("Bottles Sold"),
        ])
        .with_columns(
            (pl.col("Realised Margin %") - pl.col("Planned Margin %"))
            .round(1).alias("Margin Gap (pp)")
        )
        .to_pandas()
    )
    fig = px.scatter(
        data,
        x="Revenue (£)",
        y="Realised Margin %",
        size="Bottles Sold",
        color="Distillery Group",
        text="Distillery",
        hover_data={"Planned Margin %": True, "Margin Gap (pp)": True,
                    "Bottles Sold": True, "Distillery Group": False},
        title="Revenue vs Realised Margin % by Distillery",
        size_max=60,
    )
    fig.update_traces(textposition="top center", textfont_size=11)
    fig.update_layout(
        xaxis_tickprefix="£", xaxis_tickformat=",",
        yaxis_title="Realised Margin %",
        xaxis_title="Total Revenue (£)",
    )
    avg_rev = data["Revenue (£)"].mean()
    avg_margin = data["Realised Margin %"].mean()
    fig.add_vline(x=avg_rev, line_dash="dash", line_color="rgba(196,120,74,0.4)",
                  annotation_text="Avg revenue", annotation_position="top right")
    fig.add_hline(y=avg_margin, line_dash="dash", line_color="rgba(196,120,74,0.4)",
                  annotation_text="Avg margin", annotation_position="top right")
    return fig


# ── Revenue ──────────────────────────────────────────────────────────────────

def revenue_treemap(df: pl.DataFrame) -> go.Figure:
    data = (
        df.group_by(["Distillery Group", "Distillery"])
        .agg(pl.col("Revenue (£)").sum())
        .to_pandas()
    )
    fig = px.treemap(
        data,
        path=["Distillery Group", "Distillery"],
        values="Revenue (£)",
        title="Revenue by Distillery Group & Distillery",
        color="Revenue (£)",
        color_continuous_scale=["#3d1626", "#c4784a"],
    )
    fig.update_traces(textinfo="label+value+percent root",
                      texttemplate="<b>%{label}</b><br>£%{value:,.0f}<br>%{percentRoot:.1%}")
    fig.update_layout(coloraxis_showscale=False)
    return fig


def revenue_by_market(df: pl.DataFrame) -> go.Figure:
    data = (
        df.group_by(["Distillery", "Market"])
        .agg(pl.col("Revenue (£)").sum())
        .sort("Revenue (£)", descending=True)
        .to_pandas()
    )
    fig = px.bar(
        data, x="Distillery", y="Revenue (£)",
        color="Market", barmode="stack",
        title="Revenue by Distillery & Market",
    )
    fig.update_layout(yaxis_tickprefix="£", yaxis_tickformat=",")
    return fig
