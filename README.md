# Artisanal Spirits — Pricing Intelligence Dashboard

A Streamlit dashboard for analysing whisky pricing, margins, and sell-through data, with a natural-language AI assistant powered by Claude.

## Requirements

- [uv](https://docs.astral.sh/uv/getting-started/installation/) — Python package manager
- An [Anthropic API key](https://console.anthropic.com/) for the AI Assistant tab

## Setup

```bash
uv sync
uv run streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser. Enter your Anthropic API key in the sidebar — it is masked, never written to disk, and cleared when the session ends.

## Deploying to Streamlit Community Cloud

1. Push the repo to GitHub.
2. Create an app on [share.streamlit.io](https://share.streamlit.io) pointing at `app.py`.
3. Users enter their Anthropic API key in the sidebar — it is masked and cleared when the session ends.

## Tabs

| Tab | What it shows |
|-----|---------------|
| **Overview** | Portfolio KPIs, revenue by distillery, market comparison |
| **Pricing** | RRP vs realised price, uplift/erosion by distillery and market |
| **Volume & Revenue** | Sell-through by collection, allocation vs sold, revenue efficiency heatmap |
| **Margins** | Planned vs realised margins, gap distribution, underperformers |
| **AI Assistant** | Ask plain-English questions about the filtered dataset |

## Filters

Use the sidebar to narrow the dataset by market, distillery, collection type, and age range. All tabs — including the AI assistant — respond to the active filters.

## Project structure

```
app.py                  # Entry point (wires together src/ modules)
src/
  config.py             # Constants (model, paths, titles)
  data/
    loader.py           # Cached CSV loader
    models.py           # Dataclasses: Filters, OverviewMetrics, AppSecrets, ChatMessage
  charts/
    overview.py         # Revenue and market charts
    pricing.py          # RRP vs realised, erosion charts
    volume.py           # Sell-through, allocation, heatmap
    margins.py          # Margin gap charts and tables
  ai/
    client.py           # Anthropic client with prompt caching
  ui/
    sidebar.py          # Sidebar filters and secrets loading
    tabs/               # One render() function per tab
```
