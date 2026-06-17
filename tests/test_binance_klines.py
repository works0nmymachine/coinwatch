from datetime import date

from ingestion.binance_klines import build_url, _parse_row, insert_candles, fetch_klines

def _fixture_row() -> dict:
    """One raw CSV row, all values as strings — the shape _parse_row expects.
    open_time/close_time span 2026-06-10 00:00:00–00:00:59.999 UTC, in ms."""
    return {
        "open_time": "1781049600000", "open": "67234.50", "high": "67250.00",
        "low": "67200.10", "close": "67241.30", "volume": "12.34567",
        "close_time": "1781049659999", "quote_volume": "830123.45", "trades": "210",
        "taker_buy_base": "6.789", "taker_buy_quote": "456789.12", "ignore": "0",
    }

def test_build_url():
    assert build_url("BTCUSDT", date(2026, 6, 10)) == (
        "https://data.binance.vision/data/spot/daily/klines/"
        "BTCUSDT/1m/BTCUSDT-1m-2026-06-10.zip"
    )

def test_parse_row_converts_types():
    raw = {
        "open_time": "1749513600000", "open": "67234.50", "high": "67250.00",
        "low": "67200.10", "close": "67241.30", "volume": "12.34567",
        "close_time": "1749513659999", "quote_volume": "830123.45", "trades": "210",
        "taker_buy_base": "6.789", "taker_buy_quote": "456789.12", "ignore": "0",
    }
    parsed = _parse_row("BTCUSDT", raw)
    assert parsed["symbol"] == "BTCUSDT"
    assert parsed["open"] == 67234.50
    assert parsed["trades"] == 210
    assert parsed["open_time"].year == 2025

def test_insert_is_append_only(db_conn):
    rows = [_parse_row("BTCUSDT", _fixture_row())]
    insert_candles(db_conn, rows)
    insert_candles(db_conn, rows)  # same row again, on purpose

    with db_conn.cursor() as cur:
        cur.execute(
            "SELECT count(*) FROM raw_candles WHERE symbol='BTCUSDT' AND open_time=%s",
            (rows[0]["open_time"],),
        )
        assert cur.fetchone()[0] == 2