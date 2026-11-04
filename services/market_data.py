
import pandas as pd
import yfinance as yf

CACHE = {}


def get_history(ticker, period="6mo"):
    key = (ticker.upper(), period)

    if key in CACHE:
        return CACHE[key].copy()

    try:
        frame = yf.Ticker(ticker).history(
            period=period,
            auto_adjust=True
        )

        if frame.empty:
            return pd.DataFrame()

        frame = frame.dropna(subset=["Close"]).copy()
        frame.index = pd.to_datetime(frame.index)

        CACHE[key] = frame

        return frame.copy()

    except Exception as error:
        print(f"Market data error for {ticker}: {error}")
        return pd.DataFrame()


def get_quote(ticker):
    frame = get_history(ticker, "5d")

    if frame.empty:
        return None

    close = frame["Close"].dropna()

    latest = float(close.iloc[-1])
    previous = float(close.iloc[-2]) if len(close) > 1 else latest

    return {
        "ticker": ticker,
        "price": latest,
        "change": ((latest / previous) - 1) * 100 if previous else 0,
        "date": close.index[-1].strftime("%d %b %Y")
    }




# What does this module do?
# - get_history() retrieves historical stock prices.
# - get_quote() calculates the latest available closing price and daily percentage change.
# - CACHE avoids repeatedly downloading the same historical data during the process lifetime.