import streamlit as st
from utils.data import load_market_snapshot, load_stock_history, DEFAULT_WATCHLIST
from utils.analysis import add_indicators, stock_summary
from components.ui import inject_theme, metric_card, sidebar

st.set_page_config(page_title="StockScope", page_icon="📈", layout="wide")
inject_theme()
sidebar()

st.markdown('<div class="eyebrow">MARKET INTELLIGENCE PLATFORM</div>', unsafe_allow_html=True)
st.title("Market overview")
st.caption("A clearer view of the market. Track stocks, understand movements, and explore your portfolio.")

snapshot = load_market_snapshot()
cols = st.columns(4)
for col, item in zip(cols, snapshot):
    with col:
        metric_card(item["name"], item["value"], item["change"])

st.markdown("### Market watch")
left, right = st.columns([2.2, 1], gap="large")
with left:
    selected = st.selectbox("Explore a stock", DEFAULT_WATCHLIST, index=0, label_visibility="collapsed")
    history = load_stock_history(selected)
    if history.empty:
        st.warning("No market data returned. Check your internet connection or ticker symbol.")
    else:
        enriched = add_indicators(history)
        summary = stock_summary(enriched)
        m1, m2, m3 = st.columns(3)
        currency = "₹" if selected.endswith(".NS") else "$"
        m1.metric("Latest close", f"{currency}{summary['close']:,.2f}", f"{summary['daily_change']:+.2f}%")
        m2.metric("20-day average", f"{summary['sma20']:,.2f}")
        m3.metric("50-day average", f"{summary['sma50']:,.2f}")
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown("**Price performance**")
        st.line_chart(enriched[["Close", "SMA20", "SMA50"]].dropna(), height=330)
        st.markdown('</div>', unsafe_allow_html=True)

with right:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown("**Your watchlist**")
    for ticker in DEFAULT_WATCHLIST:
        df = load_stock_history(ticker, period="5d")
        if not df.empty:
            price = float(df["Close"].iloc[-1])
            change = ((price / float(df["Close"].iloc[-2])) - 1) * 100 if len(df) > 1 else 0
            st.markdown(f"""<div class="watch-row">
            <div><b>{ticker.replace('.NS','')}</b><div class="muted">{'NSE' if ticker.endswith('.NS') else 'US market'}</div></div>
            <div style="text-align:right"><b>{price:,.2f}</b><div class="{'positive' if change >= 0 else 'negative'}">{change:+.2f}%</div></div>
            </div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown("**StockScope insight**")
    st.write("Your AI research assistant will appear here in the next development milestone.")
    st.caption("Future insights will be grounded in retrieved market data and clearly dated.")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")
st.caption("StockScope is an informational analytics prototype, not investment advice. Development data is provided by Yahoo Finance via yfinance; commercial use requires suitable data rights.")
