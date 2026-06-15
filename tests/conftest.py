import pytest

from ingestion.db import get_connection


@pytest.fixture
def db_conn():
    conn = get_connection()
    yield conn
    conn.rollback()
    conn.close()