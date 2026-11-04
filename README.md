# StockScope

**Your Personal AI-Powered Market Intelligence Platform**

StockScope is a Python-first stock research dashboard built with NiceGUI. This starter version includes a market overview, stock history and moving averages, a persistent local watchlist, a basic portfolio cost tracker, and a rule-based research summary.

## Run locally

Python 3.10+ is recommended.

```bash
git clone https://github.com/gitofram/stockscope.git
cd stockscope
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Open http://localhost:8080.

## Features

- Market overview: NIFTY 50, SENSEX, NASDAQ and S&P 500 (where provider data is available).
- Stock analysis: historical closing prices, daily change, 20-day and 50-day simple moving averages.
- Watchlist: add/remove ticker symbols; stored in local SQLite database.
- Portfolio: record quantity and average cost; calculates invested cost only.
- Research: transparent rule-based stock summary (not an AI agent).

## Data and production limitations

- The initial market-data adapter uses yfinance for development and educational prototyping. It is not an exchange-authorized real-time feed and availability, accuracy, delay and permitted use are subject to the provider and exchange terms.
- Before offering StockScope commercially, replace or supplement this source with a market-data provider whose contract explicitly permits your intended display, redistribution and commercial use. Review applicable exchange licensing and Indian financial regulations.
- This build is a single-instance prototype. SQLite is local; watchlist and portfolio are not yet separated by customer account. Do not deploy it as a multi-customer service in its current form.
- No brokerage connection, order placement, personalized investment advice or guaranteed returns.
- The research summary is rule-based. No LLM/AI service is connected yet.

## Planned next steps

1. Add user registration, login and per-user data isolation.
2. Move application data to PostgreSQL.
3. Add licensed market data, caching and background refresh.
4. Add company news and alert preferences.
5. Add an AI research assistant with clear citations and safety boundaries.
6. Add tests, monitoring, deployment secrets and production hardening.

## Configuration

No API key is required for this prototype. Do not commit secrets to Git.
