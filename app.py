"""Artisanal Spirits Company — Pricing Intelligence Dashboard"""
import streamlit as st

from src.config import APP_TITLE, APP_ICON
from src.data.loader import load_data
from src.ui.sidebar import render_sidebar
from src.ui.tabs import overview, pricing, volume, margins, assistant

st.set_page_config(page_title=APP_TITLE, page_icon=APP_ICON, layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=Raleway:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Raleway', sans-serif !important;
}

h1, h2, h3, h4, h5, h6 {
    font-family: 'Playfair Display', serif !important;
    color: #c4784a !important;
    letter-spacing: 0.03em;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #1e0912 !important;
    border-right: 1px solid rgba(196, 120, 74, 0.25) !important;
}

/* Tabs */
[data-testid="stTabs"] button {
    font-family: 'Raleway', sans-serif !important;
    font-weight: 600 !important;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    font-size: 0.75rem !important;
}

[data-testid="stTabs"] button[aria-selected="true"] {
    color: #c4784a !important;
    border-bottom-color: #c4784a !important;
}

/* Metric cards */
[data-testid="metric-container"] {
    background-color: #3d1626;
    border: 1px solid rgba(196, 120, 74, 0.3);
    border-radius: 6px;
    padding: 1rem 1.25rem;
}

[data-testid="stMetricValue"] {
    font-family: 'Playfair Display', serif !important;
    color: #c4784a !important;
}

[data-testid="stMetricLabel"] {
    font-family: 'Raleway', sans-serif !important;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-size: 0.7rem !important;
    opacity: 0.75;
}

/* Buttons */
.stButton > button {
    font-family: 'Raleway', sans-serif !important;
    font-weight: 600 !important;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    border: 1px solid #c4784a !important;
    background-color: transparent !important;
    color: #c4784a !important;
    border-radius: 2px;
    transition: all 0.2s ease;
}

.stButton > button:hover {
    background-color: #c4784a !important;
    color: #2d0e1c !important;
}

/* Inputs and selects */
[data-testid="stSelectbox"] > div > div,
[data-testid="stMultiSelect"] > div > div,
[data-testid="stTextInput"] > div > div > input {
    border-color: rgba(196, 120, 74, 0.4) !important;
    border-radius: 2px !important;
}

/* Dividers */
hr {
    border-color: rgba(196, 120, 74, 0.2) !important;
}

/* Expanders */
[data-testid="stExpander"] {
    border: 1px solid rgba(196, 120, 74, 0.25) !important;
    border-radius: 4px;
}

/* DataFrames */
[data-testid="stDataFrame"] {
    border: 1px solid rgba(196, 120, 74, 0.25);
    border-radius: 4px;
}
</style>
""", unsafe_allow_html=True)

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
