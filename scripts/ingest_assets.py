import os

from ingestion.coingecko_assets import fetch_asset_metadata, insert_assets
from ingestion.db import get_connection

ASSET_COUNT = int(os.environ.get("ASSET_COUNT", "100"))

if __name__ == "__main__":
    conn = get_connection()
    rows = fetch_asset_metadata(ASSET_COUNT)
    insert_assets(conn,rows)
    print(f"Inserted {len(rows)} asset rows")