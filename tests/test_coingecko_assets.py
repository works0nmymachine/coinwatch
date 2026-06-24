import json
from pathlib import Path

import ingestion.coingecko_assets as cg
from ingestion.coingecko_assets import _parse_market, fetch_asset_metadata

FIXTURE = json.loads(
    (Path(__file__).parent / "fixtures" / "coingecko_markets.json").read_text()
)


class _FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        pass

    def json(self):
        return self._payload


def test_parse_market_maps_fields():
    parsed = _parse_market(FIXTURE[0])
    assert parsed == {
        "asset_id": "bitcoin",
        "symbol": "BTC",  # upper-cased
        "name": "Bitcoin",
        "market_cap_rank": 1,
    }


def test_fetch_sends_market_cap_order_and_per_page(monkeypatch):
    calls = []

    def fake_get(url, params, timeout):
        calls.append(params)
        return _FakeResponse(FIXTURE)

    monkeypatch.setattr(cg.requests, "get", fake_get)

    rows = fetch_asset_metadata(3)

    assert len(rows) == 3
    assert calls[0]["order"] == "market_cap_desc"
    assert calls[0]["per_page"] == 3
    assert calls[0]["page"] == 1


def test_fetch_paginates_and_stops_on_empty_page(monkeypatch):
    pages = {1: FIXTURE, 2: []}  # page 2 is empty -> ran out of coins

    def fake_get(url, params, timeout):
        return _FakeResponse(pages[params["page"]])

    monkeypatch.setattr(cg.requests, "get", fake_get)

    # ask for more than one page's worth; should stop when page 2 returns empty
    rows = fetch_asset_metadata(10)

    assert len(rows) == len(FIXTURE)
