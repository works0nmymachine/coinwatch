CREATE TABLE IF NOT EXISTS raw_candles (
    id              BIGSERIAL PRIMARY KEY,
    symbol          TEXT NOT NULL,
    open_time       TIMESTAMPTZ NOT NULL,
    open            NUMERIC NOT NULL,
    high            NUMERIC NOT NULL,
    low             NUMERIC NOT NULL,
    close           NUMERIC NOT NULL,
    volume          NUMERIC NOT NULL,
    close_time      TIMESTAMPTZ NOT NULL,
    quote_volume    NUMERIC NOT NULL,
    trades          INTEGER NOT NULL,
    taker_buy_base  NUMERIC NOT NULL,
    taker_buy_quote NUMERIC NOT NULL,
    ingested_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_raw_candles_symbol_time
    ON raw_candles (symbol, open_time);