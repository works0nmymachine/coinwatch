from datetime import date

from ingestion.binance_klines import fetch_klines
from ingestion.db import get_connection

if __name__ == "__main__":
    conn = get_connection()
    n = fetch_klines(conn, "BTCUSDT", date(2026, 6, 10))
    print(f"Inserted {n} rows")