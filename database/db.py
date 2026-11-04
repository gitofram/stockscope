
import os
import sqlite3
from pathlib import Path
from datetime import datetime


# ---------- Database Configuration ----------

BASE_DIR = Path(__file__).resolve().parent.parent

DB_PATH = Path(
    os.environ.get(
        "STOCKSCOPE_DB_PATH",
        str(BASE_DIR / "stockscope.db")
    )
)

DB_PATH.parent.mkdir(parents=True, exist_ok=True)

DEFAULT_TICKERS = [
    "RELIANCE.NS",
    "TCS.NS",
    "INFY.NS",
    "AAPL",
    "MSFT"
]


# ---------- Database Connection ----------

def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


# ---------- Database Initialization ----------

def init_db():
    with get_connection() as conn:

        conn.execute("""
            CREATE TABLE IF NOT EXISTS watchlist (
                ticker TEXT PRIMARY KEY,
                added_at TEXT NOT NULL
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS holdings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL,
                quantity REAL NOT NULL,
                average_price REAL NOT NULL
            )
        """)

        count = conn.execute(
            "SELECT COUNT(*) FROM watchlist"
        ).fetchone()[0]

        if count == 0:
            conn.executemany(
                """
                INSERT OR IGNORE INTO watchlist(ticker, added_at)
                VALUES (?, ?)
                """,
                [
                    (ticker, datetime.now().isoformat())
                    for ticker in DEFAULT_TICKERS
                ]
            )


# ---------- Watchlist Operations ----------

def get_watchlist():
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT ticker FROM watchlist ORDER BY ticker"
        ).fetchall()

        return [row["ticker"] for row in rows]


def add_ticker(ticker):
    ticker = ticker.strip().upper()

    if not ticker or len(ticker) > 24:
        return False

    with get_connection() as conn:
        conn.execute(
            """
            INSERT OR IGNORE INTO watchlist(ticker, added_at)
            VALUES (?, ?)
            """,
            (ticker, datetime.now().isoformat())
        )

    return True


def remove_ticker(ticker):
    with get_connection() as conn:
        conn.execute(
            "DELETE FROM watchlist WHERE ticker = ?",
            (ticker,)
        )


# ---------- Portfolio Operations ----------

def get_holdings():
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM holdings ORDER BY ticker"
        ).fetchall()

        return [dict(row) for row in rows]


def add_holding(ticker, quantity, price):
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO holdings(ticker, quantity, average_price)
            VALUES (?, ?, ?)
            """,
            (ticker.strip().upper(), float(quantity), float(price))
        )


def delete_holding(holding_id):
    with get_connection() as conn:
        conn.execute(
            "DELETE FROM holdings WHERE id = ?",
            (int(holding_id),)
        )
