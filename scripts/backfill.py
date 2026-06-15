from datetime import date, timedelta
from ingestion.binance_klines import fetch_klines
from ingestion.db import get_connection

SYMBOLS = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]
BEGINDATE = date.today()- timedelta(days=7)
ENDDATE = date.today()

if __name__ == "__main__":
    conn = get_connection()
    day = BEGINDATE
    while day <= ENDDATE:
        for symbol in SYMBOLS:
            n = fetch_klines(conn, symbol, day)
            print(f"{symbol} {day}: {n} rows")
        day += timedelta(days=1)
