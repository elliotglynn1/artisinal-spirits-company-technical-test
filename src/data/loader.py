import streamlit as st
import polars as pl

from src.config import CSV_PATH


@st.cache_data
def load_data() -> pl.DataFrame:
    df = pl.read_csv(str(CSV_PATH), null_values=["N/A"])
    return df.rename({c: c.strip() for c in df.columns})
