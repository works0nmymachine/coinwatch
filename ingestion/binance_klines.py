import csv
import io
import zipfile
from datetime import date, datetime, timezone

import requests

COLUMNS = [
    "open_time", "open", "high", "low", "close", "volume",
    "close_time", "quote_volume", "trades",
    "taker_buy_base", "taker_buy_quote", "ignore",
]

INSERT_SQL = """
    INSERT INTO raw_candles (
        symbol, open_time, open, high, low, close, volume,
        close_time, quote_volume, trades, taker_buy_base, taker_buy_quote
    ) VALUES (
        %(symbol)s, %(open_time)s, %(open)s, %(high)s, %(low)s, %(close)s, %(volume)s,
        %(close_time)s, %(quote_volume)s, %(trades)s, %(taker_buy_base)s, %(taker_buy_quote)s
    )
"""


def build_url(symbol: str, day: date) -> str:
    """Hop 0: where the file lives. See Platform Walkthrough §1.3.1."""
    d = day.isoformat()
    return (
        f"https://data.binance.vision/data/spot/daily/klines/"
        f"{symbol}/1m/{symbol}-1m-{d}.zip"
    )


def _parse_row(symbol: str, raw: dict) -> dict:
    """Turn one anonymous CSV row into typed, named values."""
    to_dt = lambda ms: datetime.fromtimestamp(int(ms) / (1_000_000 if int(ms) > 1e14 else 1000), tz=timezone.utc)
    return {
        "symbol": symbol,
        "open_time": to_dt(raw["open_time"]),
        "open": float(raw["open"]),
        "high": float(raw["high"]),
        "low": float(raw["low"]),
        "close": float(raw["close"]),
        "volume": float(raw["volume"]),
        "close_time": to_dt(raw["close_time"]),
        "quote_volume": float(raw["quote_volume"]),
        "trades": int(raw["trades"]),
        "taker_buy_base": float(raw["taker_buy_base"]),
        "taker_buy_quote": float(raw["taker_buy_quote"]),
    }


def download_klines(symbol: str, day: date) -> list[dict]:
    """Download + unzip + parse one day's klines for one symbol."""
    resp = requests.get(build_url(symbol, day), timeout=30)
    resp.raise_for_status()
    with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
        csv_name = zf.namelist()[0]
        with zf.open(csv_name) as f:
            reader = csv.reader(io.TextIOWrapper(f, encoding="utf-8"))
            return [_parse_row(symbol, dict(zip(COLUMNS, row))) for row in reader]


def insert_candles(conn, rows: list[dict]) -> None:
    """Append rows to raw_candles. No dedup here — bronze is raw on purpose."""
    with conn.cursor() as cur:
        cur.executemany(INSERT_SQL, rows)
    conn.commit()


def fetch_klines(conn, symbol: str, day: date) -> int:
    """Full hop: download one symbol/day and load it. Returns rows inserted."""
    rows = download_klines(symbol, day)
    insert_candles(conn, rows)
    return len(rows)