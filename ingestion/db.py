import os
import psycopg2


def get_connection():
    return psycopg2.connect(
        host=os.environ.get("PGHOST", "localhost"),
        port=os.environ.get("PGPORT", "5432"),
        dbname=os.environ.get("PGDATABASE", "coinwatch"),
        user=os.environ.get("PGUSER", "coinwatch"),
        password=os.environ.get("PGPASSWORD", "coinwatch"),
    )