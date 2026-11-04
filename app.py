
import os

from nicegui import ui

from database.db import (
    init_db,
    get_watchlist,
    add_ticker,
    remove_ticker,
    get_holdings,
    add_holding,
    delete_holding
)

from services.market_data import (
    get_history,
    get_quote
)


# ---------- Helper Functions ----------

def money(value):
    return f"{value:,.2f}" if value is not None else "—"


def change_label(value):
    color = "positive" if value >= 0 else "negative"
    sign = "+" if value >= 0 else ""
    return f'<span class="{color}">{sign}{value:.2f}%</span>'


# ---------- UI Styling ----------

ui.add_head_html("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap" rel="stylesheet">
<style>
:root{--bg:#080f1c;--panel:#101b2b;--line:#223249;--muted:#91a0b5;--green:#35d39a;--text:#edf3fb}
body{background:var(--bg);color:var(--text);font-family:'DM Sans',sans-serif}
.q-page{background:var(--bg)}.brand{font:700 22px 'Space Grotesk';color:#fff}
.sidebar{background:#0c1625;border-right:1px solid var(--line)}
.nav-btn{width:100%;justify-content:flex-start!important;color:#bdcadd!important;border-radius:9px!important}
.nav-btn:hover{background:#17263a!important}
.page-title{font:700 32px 'Space Grotesk';color:var(--text)}
.muted{color:var(--muted)}.panel{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:18px}
.metric{background:var(--panel);border:1px solid var(--line);border-radius:13px;padding:17px;min-width:150px;flex:1}
.metric-label{font-size:12px;color:var(--muted)}.metric-value{font:600 25px 'Space Grotesk';margin-top:8px}
.positive{color:var(--green)}.negative{color:#ff7b86}
.q-btn{border-radius:8px}.q-field--outlined .q-field__control:before{border-color:#33465f}
.q-field__native,.q-field__label{color:#eaf2fc!important}
table{color:#eaf2fc!important}.q-table{background:transparent!important}
</style>
""")


# ---------- Database Initialization ----------

init_db()


# ---------- Application Layout ----------

ui.dark_mode().enable()

with ui.left_drawer(value=True).classes("sidebar") as drawer:
    ui.label("S  StockScope").classes("brand q-mb-lg")
    ui.label("MARKET WORKSPACE").classes("text-caption muted q-mb-sm")

    def nav_button(label, icon, page):
        ui.button(
            label,
            icon=icon,
            on_click=lambda: show_page(page)
        ).props("flat").classes("nav-btn")

    nav_button("Overview", "dashboard", "overview")
    nav_button("Analyze stock", "show_chart", "analyze")
    nav_button("Watchlist", "star", "watchlist")
    nav_button("Portfolio", "account_balance_wallet", "portfolio")
    nav_button("Research", "auto_awesome", "research")

    ui.space()
    ui.label("● DATA CONNECTION · BETA").classes("text-caption muted")


with ui.header().classes("items-center justify-between").style(
    "background:#0c1625;border-bottom:1px solid #223249"
):
    ui.button(icon="menu", on_click=drawer.toggle).props("flat round")
    ui.label("MARKET INTELLIGENCE").classes("text-caption muted")
    ui.label("DEVELOPMENT BUILD").classes("text-caption muted")


content = ui.column().classes("w-full p-6")
current_page = "overview"


# ---------- Reusable UI Components ----------

def metric_card(parent, label, value, sub=None, positive=None):
    with parent:
        with ui.column().classes("metric"):
            ui.label(label).classes("metric-label")
            ui.label(value).classes("metric-value")

            if sub:
                ui.label(sub).classes(
                    "positive" if positive is True
                    else "negative" if positive is False
                    else "muted"
                )


# ---------- Overview Page ----------

def render_overview():
    ui.label("MARKET INTELLIGENCE PLATFORM").classes("text-caption positive")
    ui.label("Market overview").classes("page-title")
    ui.label(
        "Explore market movements and keep your favourite stocks in view."
    ).classes("muted")

    with ui.row().classes("w-full gap-3 q-mt-md"):
        for name, symbol in [
            ("NIFTY 50", "^NSEI"),
            ("SENSEX", "^BSESN"),
            ("NASDAQ", "^IXIC"),
            ("S&P 500", "^GSPC")
        ]:
            q = get_quote(symbol)

            with ui.column().classes("metric"):
                ui.label(name).classes("metric-label")
                ui.label(
                    money(q["price"]) if q else "Unavailable"
                ).classes("metric-value")

                if q:
                    ui.html(change_label(q["change"]))
                else:
                    ui.label("Data unavailable").classes("muted")

    ui.label("Your watchlist").classes("text-h6 q-mt-lg")

    rows = []

    for ticker in get_watchlist():
        q = get_quote(ticker)

        if q:
            rows.append({
                "ticker": ticker,
                "price": money(q["price"]),
                "change": f'{q["change"]:+.2f}%',
                "date": q["date"]
            })

    if rows:
        ui.table(
            columns=[
                {"name": "ticker", "label": "SYMBOL", "field": "ticker", "align": "left"},
                {"name": "price", "label": "LATEST CLOSE", "field": "price", "align": "left"},
                {"name": "change", "label": "CHANGE", "field": "change", "align": "left"},
                {"name": "date", "label": "DATA DATE", "field": "date", "align": "left"},
            ],
            rows=rows,
            row_key="ticker"
        ).classes("w-full panel")
    else:
        ui.label(
            "No quote data available right now. Check your internet connection or ticker symbols."
        ).classes("muted")


# ---------- Analyze Stock Page ----------

def render_analyze():
    ui.label("EQUITY RESEARCH").classes("text-caption positive")
    ui.label("Analyze a stock").classes("page-title")

    ticker_input = ui.input(
        "Ticker symbol",
        value="TCS.NS"
    ).classes("w-64")

    result = ui.column().classes("w-full")

    def analyze():
        result.clear()

        ticker = ticker_input.value.strip().upper()

        if not ticker:
            ui.notify("Enter a ticker symbol", type="warning")
            return

        with result:
            with ui.spinner():
                frame = get_history(ticker, "1y")

            if frame.empty:
                ui.label(
                    "No data found. Try TCS.NS, RELIANCE.NS, INFY.NS or AAPL."
                ).classes("negative")
                return

            close = frame["Close"].dropna()

            sma20 = close.tail(20).mean() if len(close) >= 20 else None
            sma50 = close.tail(50).mean() if len(close) >= 50 else None

            previous = (
                float(close.iloc[-2])
                if len(close) > 1
                else float(close.iloc[-1])
            )

            pct = (
                (float(close.iloc[-1]) / previous - 1) * 100
                if previous else 0
            )

            with ui.row().classes("w-full gap-3"):
                metric_card(
                    ui.row(),
                    "Latest close",
                    money(float(close.iloc[-1])),
                    close.index[-1].strftime("%d %b %Y")
                )

                metric_card(
                    ui.row(),
                    "Daily change",
                    f"{pct:+.2f}%",
                    positive=pct >= 0
                )

                metric_card(
                    ui.row(),
                    "20-day SMA",
                    money(float(sma20)) if sma20 is not None else "N/A"
                )

                metric_card(
                    ui.row(),
                    "50-day SMA",
                    money(float(sma50)) if sma50 is not None else "N/A"
                )

            ui.echart({
                "xAxis": {
                    "type": "category",
                    "data": [d.strftime("%d %b") for d in close.index]
                },
                "yAxis": {
                    "type": "value",
                    "scale": True
                },
                "tooltip": {"trigger": "axis"},
                "series": [{
                    "data": [round(float(v), 2) for v in close.values],
                    "type": "line",
                    "smooth": True,
                    "showSymbol": False,
                    "areaStyle": {"opacity": 0.12}
                }]
            }).classes("w-full h-80 panel")

            ui.label(
                "Historical prices are for research and education, not investment advice."
            ).classes("muted")

    ui.button(
        "Analyze",
        icon="search",
        on_click=analyze
    ).props("color=positive")

    analyze()


# ---------- Watchlist Page ----------

def render_watchlist():
    ui.label("YOUR MARKET").classes("text-caption positive")
    ui.label("Watchlist").classes("page-title")
    ui.label("Add symbols to your local watchlist.").classes("muted")

    with ui.row().classes("items-end"):
        ticker = ui.input(
            "Ticker",
            placeholder="e.g. TCS.NS"
        ).classes("w-64")

        def add():
            if add_ticker(ticker.value or ""):
                ticker.value = ""
                ui.notify("Watchlist updated", type="positive")
                show_page("watchlist")
            else:
                ui.notify("Enter a valid ticker", type="warning")

        ui.button(
            "Add stock",
            icon="add",
            on_click=add
        ).props("color=positive")

    for symbol in get_watchlist():
        q = get_quote(symbol)

        with ui.row().classes("panel w-full items-center justify-between"):
            with ui.column().classes("gap-0"):
                ui.label(symbol).classes("text-weight-bold")

                ui.label(
                    f'{q["date"]} · {money(q["price"])}'
                    if q else "Quote unavailable"
                ).classes("muted")

            if q:
                ui.html(change_label(q["change"]))

            ui.button(
                icon="delete",
                on_click=lambda s=symbol: (
                    remove_ticker(s),
                    show_page("watchlist")
                )
            ).props("flat round color=negative")


# ---------- Portfolio Page ----------

def render_portfolio():
    ui.label("HOLDINGS TRACKER").classes("text-caption positive")
    ui.label("Portfolio").classes("page-title")
    ui.label(
        "Record holdings and track your invested cost. "
        "No broker connection or trade execution."
    ).classes("muted")

    with ui.card().classes("panel w-full"):
        ticker = ui.input("Ticker", placeholder="e.g. INFY.NS")
        qty = ui.number("Quantity", min=0.0001, value=1)
        price = ui.number("Average purchase price", min=0.01, value=100)

        def save():
            if ticker.value and qty.value and price.value:
                add_holding(ticker.value, qty.value, price.value)
                ui.notify("Holding saved", type="positive")
                show_page("portfolio")
            else:
                ui.notify("Complete all fields", type="warning")

        ui.button(
            "Save holding",
            on_click=save
        ).props("color=positive")

    holdings = get_holdings()

    total = sum(
        h["quantity"] * h["average_price"]
        for h in holdings
    )

    with ui.row().classes("w-full"):
        metric_card(ui.row(), "Total invested cost", money(total))
        metric_card(ui.row(), "Number of holdings", str(len(holdings)))

    for holding in holdings:
        with ui.row().classes("panel w-full items-center justify-between"):
            ui.label(
                f'{holding["ticker"]} · {holding["quantity"]:g} shares × '
                f'{money(holding["average_price"])}'
            )

            ui.label(
                money(holding["quantity"] * holding["average_price"])
            ).classes("positive")

            ui.button(
                icon="delete",
                on_click=lambda i=holding["id"]: (
                    delete_holding(i),
                    show_page("portfolio")
                )
            ).props("flat round color=negative")


# ---------- Research Page ----------

def render_research():
    ui.label("RESEARCH WORKSPACE").classes("text-caption positive")
    ui.label("StockScope Analyst").classes("page-title")

    ui.label(
        "A transparent, data-grounded summary. "
        "AI integration will be added after the core data layer."
    ).classes("muted")

    ticker = ui.input(
        "Ticker symbol",
        value="TCS.NS"
    ).classes("w-64")

    output = ui.column().classes("panel w-full")

    def summarize():
        output.clear()

        frame = get_history(
            ticker.value.strip().upper(),
            "1y"
        )

        with output:
            if frame.empty:
                ui.label(
                    "No data returned. Verify the ticker and try again."
                )
                return

            close = frame["Close"].dropna()

            ui.label(
                f"Research snapshot: {ticker.value.strip().upper()}"
            ).classes("text-h6")

            ui.label(
                f'Latest available close: {money(float(close.iloc[-1]))} '
                f'on {close.index[-1].strftime("%d %b %Y")}.'
            )

            ui.label(
                f'Highest close in retrieved period: {money(float(close.max()))}.'
            )

            ui.label(
                f'Lowest close in retrieved period: {money(float(close.min()))}.'
            )

            ui.label(
                f'20-session moving average: '
                f'{money(float(close.tail(20).mean())) if len(close) >= 20 else "Insufficient data"}.'
            )

            ui.label(
                f'50-session moving average: '
                f'{money(float(close.tail(50).mean())) if len(close) >= 50 else "Insufficient data"}.'
            )

            ui.label(
                "This is a rule-based summary, not an AI-generated recommendation."
            ).classes("muted")

    ui.button(
        "Generate research summary",
        on_click=summarize
    ).props("color=positive")


# ---------- Navigation ----------

def show_page(page):
    global current_page

    current_page = page
    content.clear()

    with content:
        if page == "overview":
            render_overview()
        elif page == "analyze":
            render_analyze()
        elif page == "watchlist":
            render_watchlist()
        elif page == "portfolio":
            render_portfolio()
        else:
            render_research()


# ---------- Application Startup ----------

show_page("overview")

ui.run(
    title="StockScope",
    host="0.0.0.0",
    port=int(os.environ.get("PORT", "8080")),
    reload=False
)
