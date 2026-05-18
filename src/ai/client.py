import anthropic
import polars as pl

from src.config import AI_MODEL
from src.data.models import ChatMessage


def build_system_prompt(df: pl.DataFrame) -> str:
    return f"""You are a sharp pricing analyst for an artisanal whisky company.
You have access to the following SKU-level pricing dataset ({df.shape[0]} rows after current filters).

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
{df.to_pandas().to_csv(index=False)}

Answer questions concisely with specific numbers from the data.
Flag uncertainty where relevant. Suggest actionable follow-ups where useful."""


def get_answer(api_key: str, df: pl.DataFrame, history: list[ChatMessage], question: str) -> str:
    client = anthropic.Anthropic(api_key=api_key)
    messages = [{"role": m.role, "content": m.content} for m in history]
    messages.append({"role": "user", "content": question})
    response = client.messages.create(
        model=AI_MODEL,
        max_tokens=1024,
        system=[{
            "type": "text",
            "text": build_system_prompt(df),
            "cache_control": {"type": "ephemeral"},
        }],
        messages=messages,
    )
    return response.content[0].text
