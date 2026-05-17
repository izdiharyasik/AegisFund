# StratOS

StratOS is a modular investment intelligence dashboard for capital allocation, macro awareness, portfolio context, and risk management. It is intentionally **not** a trading terminal clone: Streamlit is view-only, while backend jobs ingest, clean, compute, and store all datasets before the UI reads them.

## What it answers

1. What is the market doing?
2. What should I care about?
3. Where should money flow?
4. What portfolio actions make sense?

## Architecture

```text
stratos/
├── frontend/                 # Streamlit app, pages, reusable view components
├── backend/
│   ├── ingestion/            # yfinance, FRED, CoinGecko, RSS jobs
│   ├── processing/           # parquet analytics transforms
│   ├── signals/              # macro and asset signal generation
│   ├── narrative/            # YAML rule-driven narrative engine
│   ├── portfolio/            # exposure, concentration, correlation analytics
│   └── scheduler/            # APScheduler job definitions
├── database/                 # SQLite schema and connection helpers
├── configs/                  # assets, thresholds, narratives, UI settings
├── cache/                    # parquet datasets
├── logs/                     # rotating application logs
└── requirements.txt
```

## Data flow

1. Backend ingestion jobs fetch from the approved sources only: yfinance, fredapi, CoinGecko, and RSS feeds.
2. Clean historical time series are written to parquet.
3. Signals, narratives, job health, watchlists, and portfolio state are written to SQLite.
4. Streamlit reads only precomputed SQLite/parquet data and performs no API calls or financial calculations.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m stratos.backend.bootstrap
streamlit run stratos/frontend/app.py
```

The bootstrap command creates deterministic demo market data and computes the initial dashboards so the UI is usable before API credentials are configured.

## Running live jobs

```bash
python -m stratos.backend.scheduler.jobs
```

Suggested cadences are encoded in APScheduler:

- Market data: every 5 minutes
- Crypto: every 2 minutes
- Macro/FRED: daily at 06:00 UTC
- News/RSS: every 10 minutes
- Signals and narratives: every 15 minutes

Set `FRED_API_KEY` in the environment to enable FRED ingestion.

## Dashboards

- Home: regime, daily changes, strongest sectors/assets, risks, opportunities, portfolio implications
- Global Macro: DXY, yields, VIX, oil, gold, Bitcoin, global indices
- Sector Rotation: SPDR sector ETF relative strength and momentum rankings
- Indonesia: JKSE, USD/IDR, major IDX and commodity-linked equities
- Crypto: BTC, ETH, dominance-ready CoinGecko snapshot, crypto momentum
- Portfolio: allocation, exposure, concentration risk, correlation overview
- Watchlist: conviction, trend, entry, TP, SL, volatility, macro alignment
