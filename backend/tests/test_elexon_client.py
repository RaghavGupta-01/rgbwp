"""Tests for ElexonClient with chunking and retries."""

from datetime import date, datetime, timezone

import httpx
import pytest

from ingestion.elexon_client import ElexonClient


def test_fetch_actuals_fuelhh_chunking():
    """Verify that FUELHH actuals query chunks date ranges and aggregates records."""
    call_log = []

    def mock_handler(request: httpx.Request) -> httpx.Response:
        call_log.append(request.url.params)
        return httpx.Response(
            200,
            json=[
                {
                    "dataset": "FUELHH",
                    "startTime": "2026-01-02T00:00:00Z",
                    "generation": 12000.0,
                }
            ],
        )

    transport = httpx.MockTransport(mock_handler)
    client = ElexonClient(transport=transport)

    records = client.fetch_actuals_fuelhh(
        date_from=date(2026, 1, 2),
        date_to=date(2026, 1, 10),
        chunk_days=5,
    )

    # 9 days with chunk_days=5 -> 2 chunks: Jan 2-6, Jan 7-10
    assert len(call_log) == 2
    assert call_log[0]["settlementDateFrom"] == "2026-01-02"
    assert call_log[0]["settlementDateTo"] == "2026-01-06"
    assert call_log[0]["fuelType"] == "WIND"

    assert call_log[1]["settlementDateFrom"] == "2026-01-07"
    assert call_log[1]["settlementDateTo"] == "2026-01-10"
    assert len(records) == 2


def test_fetch_forecasts_windfor_chunking():
    """Verify that WINDFOR forecasts query chunks publication timestamps."""
    call_log = []

    def mock_handler(request: httpx.Request) -> httpx.Response:
        call_log.append(request.url.params)
        return httpx.Response(
            200,
            json=[
                {
                    "dataset": "WINDFOR",
                    "publishTime": "2026-01-01T00:00:00Z",
                    "startTime": "2026-01-02T00:00:00Z",
                    "generation": 14500.0,
                }
            ],
        )

    transport = httpx.MockTransport(mock_handler)
    client = ElexonClient(transport=transport)

    records = client.fetch_forecasts_windfor(
        publish_from=datetime(2026, 1, 1, 0, 0, tzinfo=timezone.utc),
        publish_to=datetime(2026, 1, 3, 0, 0, tzinfo=timezone.utc),
        chunk_days=1,
    )

    # 2 days with chunk_days=1 -> 2 calls
    assert len(call_log) == 2
    assert call_log[0]["publishDateTimeFrom"] == "2026-01-01T00:00:00Z"
    assert call_log[0]["publishDateTimeTo"] == "2026-01-02T00:00:00Z"
    assert len(records) == 2


def test_retry_on_server_error():
    """Verify that retry logic retries on HTTP 500 error and recovers."""
    attempts = 0

    def mock_handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            return httpx.Response(500, text="Internal Server Error")
        return httpx.Response(200, json=[{"dataset": "FUELHH", "generation": 100.0}])

    transport = httpx.MockTransport(mock_handler)
    client = ElexonClient(transport=transport)

    records = client.fetch_actuals_fuelhh(
        date_from="2026-01-02",
        date_to="2026-01-02",
        chunk_days=1,
    )

    assert attempts == 2
    assert len(records) == 1
    assert records[0]["generation"] == 100.0


def test_retry_exhaustion_raises():
    """Verify that exceeding retries propagates the error."""
    def mock_handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(503, text="Service Unavailable")

    transport = httpx.MockTransport(mock_handler)
    client = ElexonClient(transport=transport)

    with pytest.raises(httpx.HTTPStatusError):
        client.fetch_actuals_fuelhh(
            date_from="2026-01-02",
            date_to="2026-01-02",
            chunk_days=1,
        )
