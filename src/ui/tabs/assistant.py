import streamlit as st
import polars as pl

from src.ai.client import get_answer
from src.data.models import ChatMessage

_SUGGESTIONS = [
    "Which distillery has the worst average price erosion?",
    "What collection type has the highest sell-through?",
    "Compare UK vs EU margin performance.",
    "Which SKUs have both low sell-through and high price erosion?",
    "What are the top 5 SKUs by revenue?",
]


def render(df: pl.DataFrame, api_key: str) -> None:
    st.header("AI Pricing Assistant")
    st.caption("Ask questions about the data in plain English. Answers are grounded in the current filtered dataset.")

    if not api_key:
        st.warning(
            "Add your Anthropic API key to the secrets JSON file (or set ANTHROPIC_API_KEY) to activate this tab.",
            icon="🔑",
        )
        return

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    history: list[ChatMessage] = st.session_state.chat_history

    for msg in history:
        with st.chat_message(msg.role):
            st.markdown(msg.content)

    if not history:
        st.markdown("**Quick questions to get started:**")
        cols = st.columns(len(_SUGGESTIONS))
        for i, (col, q) in enumerate(zip(cols, _SUGGESTIONS)):
            if col.button(q, key=f"sq_{i}"):
                st.session_state["_pending_q"] = q

    pending_q = st.session_state.pop("_pending_q", None)
    user_q = st.chat_input("Ask about the data...") or pending_q

    if user_q:
        history.append(ChatMessage(role="user", content=user_q))
        with st.chat_message("user"):
            st.markdown(user_q)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    answer = get_answer(api_key, df, history[:-1], user_q)
                    st.markdown(answer)
                    history.append(ChatMessage(role="assistant", content=answer))
                except Exception as e:
                    st.error(f"Error: {e}")

    if history and st.button("Clear chat"):
        st.session_state.chat_history = []
        st.rerun()
