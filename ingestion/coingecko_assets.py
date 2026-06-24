import requests

API_URL = 'https://api.coingecko.com/api/v3/'
PER_PAGE_MAX = 250  # CoinGecko caps /coins/markets per_page at 250
SQL_QUERY =  """
    INSERT INTO raw_assets (asset_id, symbol, name, market_cap_rank)
    VALUES (%(asset_id)s, %(symbol)s, %(name)s, %(market_cap_rank)s)
"""

# shape one /coins/markets item into the row we store
def _parse_market(item: dict) -> dict:
    return {
        "asset_id": item["id"],
        "symbol": item["symbol"].upper(),
        "name": item["name"],
        "market_cap_rank": item["market_cap_rank"],
    }

# fetch the top `count` assets by market cap, paginating past the 250-per-page cap
def fetch_asset_metadata (count: int) -> list[dict]:
    rows: list[dict] = []
    page = 1
    while len(rows) < count:
        resp = requests.get(
            url = f"{API_URL}coins/markets",
            params={
                "vs_currency": "USD",
                "order": "market_cap_desc",
                "per_page": min(count - len(rows), PER_PAGE_MAX),
                "page": page,
            },
            timeout=30
        )
        resp.raise_for_status()
        batch = resp.json()
        if not batch:
            break  # ran out of coins before reaching count
        rows.extend(_parse_market(item) for item in batch)
        page += 1
    return rows

# insert the metadata in the table
def insert_assets (conn,rows: list[dict]) -> None:
    with conn.cursor() as cur:
        cur.executemany(SQL_QUERY, rows)
    conn.commit()