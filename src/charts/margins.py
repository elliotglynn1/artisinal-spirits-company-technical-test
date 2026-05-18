import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import polars as pl


def _with_margin_gap(df: pl.DataFrame) -> pd.DataFrame:
    return df.with_columns(
        (pl.col("Realised Margin %") - pl.col("Planned Margin %")).alias("Margin Gap (pp)")
    ).to_pandas()


def planned_vs_realised_by_distillery(df: pl.DataFrame) -> go.Figure:
    data = (
        df.group_by("Distillery")
        .agg([
            pl.col("Planned Margin %").mean().alias("Planned"),
            pl.col("Realised Margin %").mean().alias("Realised"),
        ])
        .sort("Realised", descending=True)
        .to_pandas()
    )
    fig = go.Figure()
    fig.add_trace(go.Bar(name="Planned", x=data["Distillery"], y=data["Planned"],
                         marker_color="#60a5fa"))
    fig.add_trace(go.Bar(name="Realised", x=data["Distillery"], y=data["Realised"],
                         marker_color="#f97316"))
    fig.update_layout(barmode="group", title="Planned vs Realised Margin % by Distillery",
                      yaxis_title="Margin %")
    return fig


def margin_gap_distribution(df: pl.DataFrame) -> go.Figure:
    df_pd = _with_margin_gap(df)
    fig = px.violin(
        df_pd, x="Collection Type", y="Margin Gap (pp)",
        color="Collection Type", box=True, points="all",
        hover_data=["SKU", "Distillery"],
        title="Margin Gap Distribution by Collection Type",
    )
    fig.add_hline(y=0, line_dash="dash", line_color="rgba(150,150,150,0.6)",
                  annotation_text="No gap")
    return fig


def margin_vs_age(df: pl.DataFrame) -> go.Figure:
    df_pd = _with_margin_gap(df)
    return px.scatter(
        df_pd, x="Age", y="Realised Margin %",
        color="Collection Type", size="Revenue (£)",
        facet_col="Market",
        hover_data=["SKU", "Distillery", "Planned Margin %", "Margin Gap (pp)"],
        trendline="ols",
        title="Realised Margin % vs Age (OLS trend)",
    )


def underperformers_table(df: pl.DataFrame, threshold: float = -10.0) -> pd.DataFrame:
    df_pd = _with_margin_gap(df)
    return (
        df_pd[df_pd["Margin Gap (pp)"] < threshold]
        .sort_values("Margin Gap (pp)")[[
            "SKU", "Distillery", "Collection Type", "Market", "Age",
            "Planned Margin %", "Realised Margin %", "Margin Gap (pp)", "Revenue (£)",
        ]]
    )
