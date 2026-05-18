import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import polars as pl


def rrp_vs_realised(df: pl.DataFrame) -> go.Figure:
    df_pd = df.to_pandas()
    max_p = max(df_pd["Planned RRP (£)"].max(), df_pd["Realised Avg Price (£)"].max())
    fig = px.scatter(
        df_pd,
        x="Planned RRP (£)",
        y="Realised Avg Price (£)",
        color="Collection Type",
        hover_data=["SKU", "Distillery", "Market", "Age"],
        title="Planned RRP vs Realised Price",
        trendline="ols",
    )
    fig.add_shape(
        type="line", x0=0, y0=0, x1=max_p, y1=max_p,
        line=dict(color="rgba(150,150,150,0.5)", dash="dash", width=1.5),
    )
    fig.add_annotation(
        x=max_p * 0.78, y=max_p * 0.9,
        text="Perfect realisation", showarrow=False,
        font=dict(size=10, color="grey"),
    )
    return fig


def uplift_erosion_by_distillery(df: pl.DataFrame) -> go.Figure:
    data = (
        df.group_by("Distillery")
        .agg(pl.col("Price uplift / erosision (£)").mean().alias("Avg (£)"))
        .sort("Avg (£)")
        .to_pandas()
    )
    colors = ["#ef4444" if v < 0 else "#22c55e" for v in data["Avg (£)"]]
    fig = go.Figure(go.Bar(
        x=data["Distillery"], y=data["Avg (£)"],
        marker_color=colors,
        text=[f"£{v:+.1f}" for v in data["Avg (£)"]],
        textposition="outside",
    ))
    fig.update_layout(
        title="Average Price Uplift / Erosion by Distillery",
        yaxis_title="£", yaxis_zeroline=True,
    )
    return fig


def realisation_by_collection_market(df: pl.DataFrame) -> go.Figure:
    fig = px.box(
        df.to_pandas(),
        x="Collection Type", y="Pricing Realisation (%)",
        color="Market", points="all",
        hover_data=["SKU", "Distillery"],
        title="Price Realisation by Collection Type & Market",
    )
    fig.add_hline(y=100, line_dash="dash", line_color="rgba(150,150,150,0.6)",
                  annotation_text="100% target")
    fig.update_yaxes(ticksuffix="%")
    return fig


def worst_erosion_table(df: pl.DataFrame, n: int = 10) -> pd.DataFrame:
    data = (
        df.select([
            "SKU", "Distillery", "Collection Type", "Market", "Age",
            "Planned RRP (£)", "Realised Avg Price (£)",
            "Price uplift / erosision (£)", "Pricing Realisation (%)",
        ])
        .sort("Price uplift / erosision (£)")
        .head(n)
        .to_pandas()
    )
    data["Pricing Realisation (%)"] = data["Pricing Realisation (%)"].map(
        lambda x: f"{x:.1f}%" if x == x else "—"
    )
    data["Price uplift / erosision (£)"] = data["Price uplift / erosision (£)"].map(
        lambda x: f"£{x:+.0f}" if x == x else "—"
    )
    return data
