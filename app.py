"""Artisanal Spirits Company — Pricing Intelligence Dashboard"""
import streamlit as st

from src.config import APP_TITLE, APP_ICON
from src.data.loader import load_data
from src.ui.sidebar import render_sidebar
from src.ui.tabs import overview, pricing, volume, margins, assistant

st.set_page_config(page_title=APP_TITLE, page_icon=APP_ICON, layout="wide")

df_raw = load_data()
filters, api_key = render_sidebar(df_raw)
df = filters.apply(df_raw)

t1, t2, t3, t4, t5 = st.tabs([
    "📊 Overview", "💰 Pricing", "📦 Volume & Revenue", "📈 Margins", "🤖 AI Assistant"
])

with t1: overview.render(df)
with t2: pricing.render(df)
with t3: volume.render(df)
with t4: margins.render(df)
with t5: assistant.render(df, api_key)
