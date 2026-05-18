"""Artisanal Spirits Company — Pricing Intelligence Dashboard"""

from pathlib import Path
import json
import os
import streamlit as st
import polars as pl
import plotly.express as px
import plotly.graph_objects as go
import anthropic

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Artisanal Spirits | Pricing Intel",
    page_icon="🥃",
    layout="wide",
)

# ── Data ──────────────────────────────────────────────────────────────────────
CSV_PATH = Path(__file__).parent / "pricing_candidate_task_dataset - pricing_candidate_task_dataset.csv"

@st.cache_data
def load_data() -> pl.DataFrame:
    df = pl.read_csv(str(CSV_PATH), null_values=["N/A"])
    df = df.rename({c: c.strip() for c in df.columns})
    return df


df_raw = load_data()

# ── Sidebar filters ────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🥃 Pricing Intelligence")
    st.caption("Artisanal Spirits Company")
    st.divider()

    st.markdown("### Filters")

    mkt_opts = ["All"] + sorted(df_raw["Market"].unique().to_list())
    sel_market = st.selectbox("Market", mkt_opts)

    dist_opts = sorted(df_raw["Distillery"].unique().to_list())
    sel_dist = st.multiselect("Distillery", dist_opts, default=dist_opts)

    coll_opts = sorted(df_raw["Collection Type"].unique().to_list())
    sel_coll = st.multiselect("Collection Type", coll_opts, default=coll_opts)

    age_min, age_max = int(df_raw["Age"].min()), int(df_raw["Age"].max())
    sel_age = st.slider("Age (years)", age_min, age_max, (age_min, age_max))

    st.divider()
    st.markdown("### 🤖 AI Assistant")
    _default_secrets = str(Path(__file__).parent / "secrets.json")
    secrets_path_input = st.text_input(
        "Secrets JSON path",
        placeholder="secrets.json",
        value=_default_secrets,
    )

# ── Apply filters ─────────────────────────────────────────────────────────────
mask = (
    pl.col("Distillery").is_in(sel_dist)
    & pl.col("Collection Type").is_in(sel_coll)
    & pl.col("Age").is_between(sel_age[0], sel_age[1])
)
if sel_market != "All":
    mask = mask & (pl.col("Market") == sel_market)

df = df_raw.filter(mask)

# ── Tabs ───────────────────────────────────────────────────────────────────────
t1, t2, t3, t4, t5 = st.tabs(
    ["📊 Overview", "💰 Pricing", "📦 Volume & Revenue", "📈 Margins", "🤖 AI Assistant"]
)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — OVERVIEW
# ═══════════════════════════════════════════════════════════════════════════════
with t1:
    st.header("Portfolio Overview")

    n_skus = df.shape[0]
    total_rev = df["Revenue (£)"].sum()
    avg_sell_through = df["Sell Through (%)"].mean()
    avg_price_real = df["Pricing Realisation (%)"].mean()
    avg_margin_gap = (df["Realised Margin %"] - df["Planned Margin %"]).mean()

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("SKUs", n_skus)
    c2.metric("Total Revenue", f"£{total_rev:,.0f}")
    c3.metric("Avg Sell-Through", f"{avg_sell_through:.1f}%")
    c4.metric("Avg Price Realisation", f"{avg_price_real:.1f}%")
    c5.metric(
        "Avg Margin Gap",
        f"{avg_margin_gap:+.1f} pp",
        delta_color="inverse",
    )

    st.divider()
    col_l, col_r = st.columns(2)

    with col_l:
        rev_by_dist = (
            df.group_by("Distillery")
            .agg(pl.col("Revenue (£)").sum())
            .sort("Revenue (£)", descending=True)
            .to_pandas()
        )
        fig = px.bar(
            rev_by_dist,
            x="Distillery",
            y="Revenue (£)",
            color="Distillery",
            title="Revenue by Distillery",
        )
        fig.update_layout(showlegend=False, yaxis_tickprefix="£", yaxis_tickformat=",")
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        rev_by_coll = (
            df.group_by("Collection Type")
            .agg(pl.col("Revenue (£)").sum())
            .sort("Revenue (£)", descending=True)
            .to_pandas()
        )
        fig = px.pie(
            rev_by_coll,
            names="Collection Type",
            values="Revenue (£)",
            title="Revenue Share by Collection Type",
            hole=0.42,
        )
        st.plotly_chart(fig, use_container_width=True)

    # Market comparison table
    st.subheader("Market Comparison")
    mkt_tbl = (
        df.group_by("Market")
        .agg(
            [
                pl.len().alias("SKUs"),
                pl.col("Revenue (£)").sum().alias("Revenue (£)"),
                pl.col("Bottles Allocated").sum().alias("Bottles Allocated"),
                pl.col("Bottles Sold").sum().alias("Bottles Sold"),
                pl.col("Sell Through (%)").mean().round(1).alias("Avg Sell-Through %"),
                pl.col("Pricing Realisation (%)").mean().round(1).alias("Avg Price Realisation %"),
                (pl.col("Realised Margin %") - pl.col("Planned Margin %"))
                .mean()
                .round(1)
                .alias("Avg Margin Gap (pp)"),
            ]
        )
        .sort("Market")
    )
    st.dataframe(
        mkt_tbl.to_pandas().set_index("Market"),
        use_container_width=True,
    )

    with st.expander("⚠️ Raw data quality notes"):
        st.markdown(
            """
**Column encoding quirks:**
- `Margin %` columns are stored as whole integers (42 = 42%)
- `Days to Sell Out` is `N/A` for items not yet sold out — treated as null
"""
        )


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — PRICING
# ═══════════════════════════════════════════════════════════════════════════════
with t2:
    st.header("Pricing Performance")

    col_l, col_r = st.columns(2)

    with col_l:
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
            type="line",
            x0=0, y0=0, x1=max_p, y1=max_p,
            line=dict(color="rgba(150,150,150,0.5)", dash="dash", width=1.5),
        )
        fig.add_annotation(
            x=max_p * 0.78, y=max_p * 0.9,
            text="Perfect realisation",
            showarrow=False,
            font=dict(size=10, color="grey"),
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        eros = (
            df.group_by("Distillery")
            .agg(pl.col("Price uplift / erosision (£)").mean().alias("Avg (£)"))
            .sort("Avg (£)")
            .to_pandas()
        )
        bar_colors = ["#ef4444" if v < 0 else "#22c55e" for v in eros["Avg (£)"]]
        fig = go.Figure(
            go.Bar(
                x=eros["Distillery"],
                y=eros["Avg (£)"],
                marker_color=bar_colors,
                text=[f"£{v:+.1f}" for v in eros["Avg (£)"]],
                textposition="outside",
            )
        )
        fig.update_layout(
            title="Average Price Uplift / Erosion by Distillery",
            yaxis_title="£",
            yaxis_zeroline=True,
        )
        st.plotly_chart(fig, use_container_width=True)

    # Box plot: price realisation by collection × market
    fig = px.box(
        df.to_pandas(),
        x="Collection Type",
        y="Pricing Realisation (%)",
        color="Market",
        points="all",
        hover_data=["SKU", "Distillery"],
        title="Price Realisation by Collection Type & Market",
    )
    fig.add_hline(
        y=100,
        line_dash="dash",
        line_color="rgba(150,150,150,0.6)",
        annotation_text="100% target",
    )
    fig.update_yaxes(ticksuffix="%")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Largest Price Erosion — Top 10 SKUs")
    worst = (
        df.select(
            [
                "SKU", "Distillery", "Collection Type", "Market", "Age",
                "Planned RRP (£)", "Realised Avg Price (£)",
                "Price uplift / erosision (£)", "Pricing Realisation (%)",
            ]
        )
        .sort("Price uplift / erosision (£)")
        .head(10)
        .to_pandas()
    )
    worst["Pricing Realisation (%)"] = worst["Pricing Realisation (%)"].map(
        lambda x: f"{x:.1f}%" if x == x else "—"
    )
    worst["Price uplift / erosision (£)"] = worst["Price uplift / erosision (£)"].map(
        lambda x: f"£{x:+.0f}" if x == x else "—"
    )
    st.dataframe(worst, use_container_width=True, hide_index=True)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — VOLUME & REVENUE
# ═══════════════════════════════════════════════════════════════════════════════
with t3:
    st.header("Volume & Revenue Analysis")

    col_l, col_r = st.columns(2)

    with col_l:
        st_coll = (
            df.group_by(["Collection Type", "Market"])
            .agg(pl.col("Sell Through (%)").mean().alias("Avg Sell-Through %"))
            .sort("Avg Sell-Through %", descending=True)
            .to_pandas()
        )
        fig = px.bar(
            st_coll,
            x="Collection Type",
            y="Avg Sell-Through %",
            color="Market",
            barmode="group",
            title="Average Sell-Through % by Collection & Market",
        )
        fig.add_hline(
            y=100,
            line_dash="dash",
            line_color="rgba(150,150,150,0.5)",
            annotation_text="Full sell-through",
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        df_pd2 = df.to_pandas()
        max_b = max(df_pd2["Bottles Allocated"].max(), df_pd2["Bottles Sold"].max())
        fig = px.scatter(
            df_pd2,
            x="Bottles Allocated",
            y="Bottles Sold",
            color="Distillery",
            size="Revenue (£)",
            hover_data=["SKU", "Collection Type", "Market", "Sell Through (%)"],
            title="Allocation vs Bottles Sold (sized by Revenue)",
        )
        fig.add_shape(
            type="line",
            x0=0, y0=0, x1=max_b, y1=max_b,
            line=dict(color="rgba(150,150,150,0.5)", dash="dash"),
        )
        st.plotly_chart(fig, use_container_width=True)

    # Revenue efficiency heatmap
    st.subheader("Revenue Efficiency Heatmap")
    st.caption("Revenue efficiency = Realised Price × Sell-Through  (higher = better)")

    rev_eff_pd = (
        df.group_by(["Distillery", "Collection Type"])
        .agg(pl.col("Revenue efficiency").mean().alias("Revenue Efficiency"))
        .to_pandas()
        .pivot(index="Distillery", columns="Collection Type", values="Revenue Efficiency")
    )
    fig = px.imshow(
        rev_eff_pd,
        text_auto=".0f",
        color_continuous_scale="RdYlGn",
        title="Revenue Efficiency by Distillery & Collection Type",
        aspect="auto",
    )
    st.plotly_chart(fig, use_container_width=True)

    # Low sell-through outliers
    st.subheader("Low Sell-Through SKUs  (< 60%)")
    low_st = (
        df.filter(pl.col("Sell Through (%)") < 60)
        .select(
            [
                "SKU", "Distillery", "Collection Type", "Market", "Age",
                "Bottles Allocated", "Bottles Sold", "Sell Through (%)", "Revenue (£)",
            ]
        )
        .sort("Sell Through (%)")
        .to_pandas()
    )
    if low_st.empty:
        st.info("No SKUs below 60% sell-through in current selection.")
    else:
        low_st["Sell Through (%)"] = low_st["Sell Through (%)"].map(lambda x: f"{x:.0f}%")
        st.dataframe(low_st, use_container_width=True, hide_index=True)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4 — MARGINS
# ═══════════════════════════════════════════════════════════════════════════════
with t4:
    st.header("Margin Analysis")

    df_m = df.with_columns(
        (pl.col("Realised Margin %") - pl.col("Planned Margin %")).alias("Margin Gap (pp)")
    ).to_pandas()

    col_l, col_r = st.columns(2)

    with col_l:
        mg_dist = (
            df.group_by("Distillery")
            .agg(
                [
                    pl.col("Planned Margin %").mean().alias("Planned"),
                    pl.col("Realised Margin %").mean().alias("Realised"),
                ]
            )
            .sort("Realised", descending=True)
            .to_pandas()
        )
        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                name="Planned",
                x=mg_dist["Distillery"],
                y=mg_dist["Planned"],
                marker_color="#60a5fa",
            )
        )
        fig.add_trace(
            go.Bar(
                name="Realised",
                x=mg_dist["Distillery"],
                y=mg_dist["Realised"],
                marker_color="#f97316",
            )
        )
        fig.update_layout(
            barmode="group",
            title="Planned vs Realised Margin % by Distillery",
            yaxis_title="Margin %",
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        fig = px.violin(
            df_m,
            x="Collection Type",
            y="Margin Gap (pp)",
            color="Collection Type",
            box=True,
            points="all",
            hover_data=["SKU", "Distillery"],
            title="Margin Gap Distribution by Collection Type",
        )
        fig.add_hline(
            y=0,
            line_dash="dash",
            line_color="rgba(150,150,150,0.6)",
            annotation_text="No gap",
        )
        st.plotly_chart(fig, use_container_width=True)

    # Margin vs age, faceted by market
    fig = px.scatter(
        df_m,
        x="Age",
        y="Realised Margin %",
        color="Collection Type",
        size="Revenue (£)",
        facet_col="Market",
        hover_data=["SKU", "Distillery", "Planned Margin %", "Margin Gap (pp)"],
        trendline="ols",
        title="Realised Margin % vs Age (OLS trend)",
    )
    st.plotly_chart(fig, use_container_width=True)

    # Underperformers
    st.subheader("Margin Underperformers  (gap < −10 pp)")
    under = df_m[df_m["Margin Gap (pp)"] < -10].sort_values("Margin Gap (pp)")[
        [
            "SKU", "Distillery", "Collection Type", "Market", "Age",
            "Planned Margin %", "Realised Margin %", "Margin Gap (pp)", "Revenue (£)",
        ]
    ]
    if under.empty:
        st.info("No SKUs with a margin gap below −10 pp in the current selection.")
    else:
        st.dataframe(under, use_container_width=True, hide_index=True)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 5 — AI ASSISTANT
# ═══════════════════════════════════════════════════════════════════════════════
with t5:
    st.header("AI Pricing Assistant")
    st.caption("Ask questions about the data in plain English. Answers are grounded in the current filtered dataset.")

    api_key = ""
    try:
        p = Path(secrets_path_input.strip()).expanduser()
        api_key = json.loads(p.read_text()).get("anthropic_api_key", "")
    except Exception:
        pass
    if not api_key:
        api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        st.warning("Add your Anthropic API key to the secrets JSON file (or set ANTHROPIC_API_KEY) to activate this tab.", icon="🔑")
        st.stop()

    def build_system_prompt(data: pl.DataFrame) -> str:
        return f"""You are a sharp pricing analyst for an artisanal whisky company.
You have access to the following SKU-level pricing dataset ({data.shape[0]} rows after current filters).

COLUMN REFERENCE:
- SKU: product identifier
- Distillery: producer name
- Distillery Group: owner group (A–G)
- Age: age of whisky in years
- Collection Type: product tier (Core / Heresy / CC / VC / Creators Collection / Vaults Collection)
- Market: UK or EU
- Planned RRP (£): intended retail price
- Realised Avg Price (£): actual average selling price achieved
- Bottles Allocated: number of bottles made available
- Bottles Sold: number of bottles actually sold
- Planned Margin %: expected margin (stored as whole number, e.g. 42 = 42%)
- Realised Margin %: actual margin achieved (same encoding)
- Days to Sell Out: days until fully sold out (null = not yet sold out)
- Sell Through (%): proportion of allocation sold as a percentage (100 = fully sold)
- Pricing Realisation (%): Realised Price / Planned RRP as a percentage (100 = full realisation)
- Price uplift / erosision (£): Realised minus Planned price (negative = erosion)
- Revenue efficiency: Realised Price × (Sell Through / 100)
- Revenue (£): total revenue for this SKU

DATASET (CSV):
{data.to_pandas().to_csv(index=False)}

Answer questions concisely with specific numbers from the data.
Flag uncertainty where relevant. Suggest actionable follow-ups where useful."""

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if not st.session_state.chat_history:
        st.markdown("**Quick questions to get started:**")
        suggestions = [
            "Which distillery has the worst average price erosion?",
            "What collection type has the highest sell-through?",
            "Compare UK vs EU margin performance.",
            "Which SKUs have both low sell-through and high price erosion?",
            "What are the top 5 SKUs by revenue?",
        ]
        cols = st.columns(len(suggestions))
        for i, (col, q) in enumerate(zip(cols, suggestions)):
            if col.button(q, key=f"sq_{i}"):
                st.session_state["_pending_q"] = q

    pending_q = st.session_state.pop("_pending_q", None)
    user_q = st.chat_input("Ask about the data...") or pending_q

    if user_q:
        st.session_state.chat_history.append({"role": "user", "content": user_q})
        with st.chat_message("user"):
            st.markdown(user_q)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    client = anthropic.Anthropic(api_key=api_key)
                    prior = st.session_state.chat_history[:-1]
                    messages = [{"role": m["role"], "content": m["content"]} for m in prior]
                    messages.append({"role": "user", "content": user_q})
                    response = client.messages.create(
                        model="claude-haiku-4-5",
                        max_tokens=1024,
                        system=[{
                            "type": "text",
                            "text": build_system_prompt(df),
                            "cache_control": {"type": "ephemeral"},
                        }],
                        messages=messages,
                    )
                    answer = response.content[0].text
                    st.markdown(answer)
                    st.session_state.chat_history.append({"role": "assistant", "content": answer})
                except Exception as e:
                    st.error(f"Error: {e}")

    if st.session_state.chat_history:
        if st.button("Clear chat"):
            st.session_state.chat_history = []
            st.rerun()
