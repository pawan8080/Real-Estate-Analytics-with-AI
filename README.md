# 🏡 AskEstate — Natural Language Analytics for Real Estate

> Ask real estate data questions in plain English. An LLM translates them to SQL, runs them safely, and visualizes the result.

AskEstate is a lightweight BI tool that demonstrates a **text-to-SQL analytics pattern** applied to real estate data. Users type questions like *"What's the average price per square foot by city?"* and get back an answer, the generated SQL, and an auto-generated chart.

## Why this project

Business intelligence teams spend a lot of time writing repetitive SQL for ad-hoc questions. This project shows one way to reduce that load: a schema-aware LLM that generates safe SQL on demand, with guardrails against destructive operations.

Built to demonstrate:

- **Text-to-SQL with LLMs** — prompt engineering, schema grounding, hallucination handling
- **SQL safety guardrails** — whitelist-based validation, single-statement enforcement, forbidden-keyword filtering
- **End-to-end analytics UX** — natural language input → SQL → results → visualization
- **Production hygiene** — CI, schema documentation, clean separation of concerns

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐     ┌────────────┐
│  Streamlit  │────▶│ Claude (LLM) │────▶│   Safety    │────▶│  SQLite    │
│    UI       │     │  text-to-SQL │     │   Check     │     │  Database  │
└─────────────┘     └──────────────┘     └─────────────┘     └────────────┘
       ▲                                                            │
       └────────────────── Results + Plotly chart ──────────────────┘
```

## Features

- **Natural language queries** against a 2,000-row real estate database
- **Schema-aware prompting** so the LLM knows column names, value domains, and types
- **SQL transparency** — the generated query is always shown to the user
- **Safety layer** that rejects `INSERT`, `UPDATE`, `DELETE`, `DROP`, multi-statement queries, and anything that isn't a single `SELECT`/`WITH`
- **Auto-visualization** of query results when the shape fits a bar chart
- **Example queries** and **query history** in the sidebar
- **GitHub Actions CI** that lints, syntax-checks, and tests the safety guardrails on every push

## Tech stack

| Layer       | Tool                      |
|-------------|---------------------------|
| Frontend    | Streamlit                 |
| LLM         | Anthropic Claude          |
| Database    | SQLite                    |
| Dataframes  | pandas                    |
| Charts      | Plotly                    |
| CI          | GitHub Actions + ruff     |

## Getting started

### 1. Clone and install

```bash
git clone https://github.com/YOUR_USERNAME/askestate.git
cd askestate
pip install -r requirements.txt
```

### 2. Set your API key

```bash
cp .env.example .env
# Open .env and paste your Anthropic API key
```

Get a key at [console.anthropic.com](https://console.anthropic.com).

### 3. Generate the dataset

```bash
python generate_data.py
```

This creates `data/real_estate.csv` with 2,000 synthetic listings across 5 cities.

### 4. Run the app

```bash
streamlit run app.py
```

The app opens at `http://localhost:8501`.

## Example questions

- *"What's the average price per square foot by city?"*
- *"Show me the 10 most expensive condos in Downtown"*
- *"How many properties sold in each neighborhood last year?"*
- *"What's the average days on market by property type?"*
- *"Compare median prices of houses built before 2000 vs after"*

## Project structure

```
askestate/
├── app.py               # Streamlit UI
├── llm.py               # Text-to-SQL via Claude + safety checks
├── database.py          # SQLite setup and query execution
├── generate_data.py     # Synthetic dataset generator
├── data/
│   └── real_estate.csv  # Generated sample data
├── requirements.txt
├── .env.example
└── .github/workflows/ci.yml
```

## Safety design

The LLM is prompted to output only `SELECT` queries, but prompts are not a security boundary. The safety layer (`is_safe_sql` in `llm.py`) enforces three rules before any query reaches the database:

1. Query must start with `SELECT` or `WITH`
2. No semicolons (single statement only)
3. No forbidden keywords: `INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, `CREATE`, `ATTACH`, `DETACH`, `PRAGMA`, `REPLACE`, `TRUNCATE`

These checks run in CI on every push.

## Limitations & next steps

- **Synthetic data**: the dataset is generated, not real MLS data. Connecting to a live data source is a natural next step.
- **Single-table schema**: real BI workloads involve joins across many tables. A multi-table version would test schema-grounding more rigorously.
- **No result caching**: each question hits the LLM fresh. Caching identical questions would cut latency and cost.
- **No unit tests on SQL generation quality**: adding an eval set of (question, expected SQL) pairs would quantify accuracy over time.

## License

MIT
