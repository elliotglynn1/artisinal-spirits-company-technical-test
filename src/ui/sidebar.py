from pathlib import Path

import polars as pl
import streamlit as st

from src.config import DEFAULT_SECRETS_PATH
from src.data.models import AppSecrets, Filters


def render_sidebar(df: pl.DataFrame) -> tuple[Filters, str]:
    with st.sidebar:
        st.markdown("## 🥃 Pricing Intelligence")
        st.caption("Artisanal Spirits Company")
        st.divider()

        st.markdown("### Filters")

        market = st.selectbox(
            "Market",
            ["All"] + sorted(df["Market"].unique().to_list()),
        )
        distilleries = st.multiselect(
            "Distillery",
            options := sorted(df["Distillery"].unique().to_list()),
            default=options,
        )
        collection_types = st.multiselect(
            "Collection Type",
            copts := sorted(df["Collection Type"].unique().to_list()),
            default=copts,
        )
        age_lo, age_hi = int(df["Age"].min()), int(df["Age"].max())
        age_range = st.slider("Age (years)", age_lo, age_hi, (age_lo, age_hi))

        st.divider()
        st.markdown("### 🤖 AI Assistant")
        secrets_path = st.text_input(
            "Secrets JSON path",
            placeholder="secrets.json",
            value=str(DEFAULT_SECRETS_PATH),
        )

    filters = Filters(
        market=market,
        distilleries=distilleries,
        collection_types=collection_types,
        age_min=age_range[0],
        age_max=age_range[1],
    )
    secrets = AppSecrets.load(Path(secrets_path.strip()).expanduser())
    return filters, secrets.anthropic_api_key
