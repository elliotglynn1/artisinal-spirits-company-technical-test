import io

import polars as pl
import streamlit as st

from src.data.models import Filters


def _get_api_key() -> str:
    return st.text_input(
        "Anthropic API key",
        type="password",
        placeholder="sk-ant-...",
        help="Never stored — lives only in your browser session.",
    )


def _excel_bytes(df: pl.DataFrame) -> bytes:
    buf = io.BytesIO()
    df.to_pandas().to_excel(buf, index=False, engine="openpyxl")
    return buf.getvalue()


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
        api_key = _get_api_key()

        st.divider()
        st.markdown("### Export")
        filters = Filters(
            market=market,
            distilleries=distilleries,
            collection_types=collection_types,
            age_min=age_range[0],
            age_max=age_range[1],
        )
        filtered_df = filters.apply(df)
        st.download_button(
            label=f"Download filtered data ({len(filtered_df)} rows)",
            data=_excel_bytes(filtered_df),
            file_name="artisanal_spirits_pricing.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

    return filters, api_key
