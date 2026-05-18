import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import polars as pl


def revenue_by_distillery(df: pl.DataFrame) -> go.Figure:
    data = (
        df.group_by("Distillery")
        .agg(pl.col("Revenue (£)").sum())
        .sort("Revenue (£)", descending=True)
        .to_pandas()
    )
    fig = px.bar(data, x="Distillery", y="Revenue (£)", color="Distillery",
                 title="Revenue by Distillery")
    fig.update_layout(showlegend=False, yaxis_tickprefix="£", yaxis_tickformat=",")
    return fig


def revenue_share_by_collection(df: pl.DataFrame) -> go.Figure:
    data = (
        df.group_by("Collection Type")
        .agg(pl.col("Revenue (£)").sum())
        .sort("Revenue (£)", descending=True)
        .to_pandas()
    )
    return px.pie(data, names="Collection Type", values="Revenue (£)",
                  title="Revenue Share by Collection Type", hole=0.42)


def market_comparison(df: pl.DataFrame) -> pd.DataFrame:
    return (
        df.group_by("Market")
        .agg([
            pl.len().alias("SKUs"),
            pl.col("Revenue (£)").sum().alias("Revenue (£)"),
            pl.col("Bottles Allocated").sum().alias("Bottles Allocated"),
            pl.col("Bottles Sold").sum().alias("Bottles Sold"),
            pl.col("Sell Through (%)").mean().round(1).alias("Avg Sell-Through %"),
            pl.col("Pricing Realisation (%)").mean().round(1).alias("Avg Price Realisation %"),
            (pl.col("Realised Margin %") - pl.col("Planned Margin %"))
            .mean().round(1).alias("Avg Margin Gap (pp)"),
        ])
        .sort("Market")
        .to_pandas()
        .set_index("Market")
    )
