import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import polars as pl


def sell_through_by_collection_market(df: pl.DataFrame) -> go.Figure:
    data = (
        df.group_by(["Collection Type", "Market"])
        .agg(pl.col("Sell Through (%)").mean().alias("Avg Sell-Through %"))
        .sort("Avg Sell-Through %", descending=True)
        .to_pandas()
    )
    fig = px.bar(
        data, x="Collection Type", y="Avg Sell-Through %",
        color="Market", barmode="group",
        title="Average Sell-Through % by Collection & Market",
    )
    fig.add_hline(y=100, line_dash="dash", line_color="rgba(150,150,150,0.5)",
                  annotation_text="Full sell-through")
    return fig


def allocation_vs_sold(df: pl.DataFrame) -> go.Figure:
    df_pd = df.to_pandas()
    max_b = max(df_pd["Bottles Allocated"].max(), df_pd["Bottles Sold"].max())
    fig = px.scatter(
        df_pd,
        x="Bottles Allocated", y="Bottles Sold",
        color="Distillery", size="Revenue (£)",
        hover_data=["SKU", "Collection Type", "Market", "Sell Through (%)"],
        title="Allocation vs Bottles Sold (sized by Revenue)",
    )
    fig.add_shape(
        type="line", x0=0, y0=0, x1=max_b, y1=max_b,
        line=dict(color="rgba(150,150,150,0.5)", dash="dash"),
    )
    return fig


def revenue_efficiency_heatmap(df: pl.DataFrame) -> go.Figure:
    pivot = (
        df.group_by(["Distillery", "Collection Type"])
        .agg(pl.col("Revenue efficiency").mean().alias("Revenue Efficiency"))
        .to_pandas()
        .pivot(index="Distillery", columns="Collection Type", values="Revenue Efficiency")
    )
    return px.imshow(
        pivot, text_auto=".0f",
        color_continuous_scale="RdYlGn",
        title="Revenue Efficiency by Distillery & Collection Type",
        aspect="auto",
    )


def low_sell_through_table(df: pl.DataFrame, threshold: float = 60.0) -> pd.DataFrame:
    data = (
        df.filter(pl.col("Sell Through (%)") < threshold)
        .select([
            "SKU", "Distillery", "Collection Type", "Market", "Age",
            "Bottles Allocated", "Bottles Sold", "Sell Through (%)", "Revenue (£)",
        ])
        .sort("Sell Through (%)")
        .to_pandas()
    )
    if not data.empty:
        data["Sell Through (%)"] = data["Sell Through (%)"].map(lambda x: f"{x:.0f}%")
    return data
