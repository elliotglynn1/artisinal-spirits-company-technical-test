from __future__ import annotations

from dataclasses import dataclass

import polars as pl


@dataclass
class Filters:
    market: str
    distilleries: list[str]
    collection_types: list[str]
    age_min: int
    age_max: int

    def apply(self, df: pl.DataFrame) -> pl.DataFrame:
        mask = (
            pl.col("Distillery").is_in(self.distilleries)
            & pl.col("Collection Type").is_in(self.collection_types)
            & pl.col("Age").is_between(self.age_min, self.age_max)
        )
        if self.market != "All":
            mask = mask & (pl.col("Market") == self.market)
        return df.filter(mask)


@dataclass
class OverviewMetrics:
    n_skus: int
    # demand
    total_bottles_sold: int
    n_sold_out: int
    avg_sell_through: float
    # pricing efficiency
    avg_price_realisation: float
    avg_price_uplift: float
    # profit
    avg_planned_margin: float
    avg_realised_margin: float
    avg_margin_gap: float
    # revenue
    total_revenue: float

    @classmethod
    def from_df(cls, df: pl.DataFrame) -> "OverviewMetrics":
        return cls(
            n_skus=df.shape[0],
            total_bottles_sold=int(df["Bottles Sold"].sum() or 0),
            n_sold_out=int(df.filter(pl.col("Sell Through (%)") == 100).shape[0]),
            avg_sell_through=df["Sell Through (%)"].mean() or 0.0,
            avg_price_realisation=df["Pricing Realisation (%)"].mean() or 0.0,
            avg_price_uplift=df["Price uplift / erosision (£)"].mean() or 0.0,
            avg_planned_margin=df["Planned Margin %"].mean() or 0.0,
            avg_realised_margin=df["Realised Margin %"].mean() or 0.0,
            avg_margin_gap=(df["Realised Margin %"] - df["Planned Margin %"]).mean() or 0.0,
            total_revenue=df["Revenue (£)"].sum() or 0.0,
        )


@dataclass
class ChatMessage:
    role: str  # "user" | "assistant"
    content: str
