from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path

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
    total_revenue: float
    avg_sell_through: float
    avg_price_realisation: float
    avg_margin_gap: float

    @classmethod
    def from_df(cls, df: pl.DataFrame) -> OverviewMetrics:
        return cls(
            n_skus=df.shape[0],
            total_revenue=df["Revenue (£)"].sum() or 0.0,
            avg_sell_through=df["Sell Through (%)"].mean() or 0.0,
            avg_price_realisation=df["Pricing Realisation (%)"].mean() or 0.0,
            avg_margin_gap=(df["Realised Margin %"] - df["Planned Margin %"]).mean() or 0.0,
        )


@dataclass
class AppSecrets:
    anthropic_api_key: str = ""

    @classmethod
    def load(cls, path: Path) -> AppSecrets:
        try:
            data = json.loads(path.read_text())
            key = data.get("anthropic_api_key", "")
            if key:
                return cls(anthropic_api_key=key)
        except Exception:
            pass
        return cls(anthropic_api_key=os.environ.get("ANTHROPIC_API_KEY", ""))


@dataclass
class ChatMessage:
    role: str  # "user" | "assistant"
    content: str
