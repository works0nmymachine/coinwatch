from datetime import date

from ingestion.binance_klines import build_url, _parse_row, insert_candles, fetch_klines

def test