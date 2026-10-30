"""Tests for ingestion cleaning and validation."""

import pandas as pd
import pytest

from ingestion.cleaning import clean_actuals, clean_forecasts


def test_clean_actuals_dedupes_and_parses():
    """Verify clean_actuals enforces UTC, dedupes on start_time, and sorts."""
    raw = [
        {
            "startTime": "2026-01-02T01:00:00Z",
            "generation": 10500.0,
            "settlementDate": "2026-01-02",
            "settlementPeriod": 3,
        },
        {
            "startTime": "2026-01-02T00:30:00Z",
            "generation": 10200.0,
            "settlementDate": "2026-01-02",
            "settlementPeriod": 2,
        },
        # Duplicate start_time
        {
            "startTime": "2026-01-02T00:30:00Z",
            "generation": 10200.0,
            "settlementDate": "2026-01-02",
            "settlementPeriod": 2,
        },
    ]

    cleaned = clean_actuals(raw)

    assert len(cleaned) == 2
    assert str(cleaned["start_time"].dt.tz) == "UTC"
    assert cleaned.iloc[0]["start_time"] == pd.Timestamp("2026-01-02 00:30:00+00:00")
    assert cleaned.iloc[1]["start_time"] == pd.Timestamp("2026-01-02 01:00:00+00:00")
    assert cleaned.iloc[0]["generation_mw"] == 10200.0
    assert cleaned.iloc[0]["settlement_period"] == 2


def test_clean_actuals_rejects_negative_generation():
    """Verify clean_actuals raises ValueError on negative generation."""
    raw = [
        {"startTime": "2026-01-02T00:00:00Z", "generation": -15.0},
    ]
    with pytest.raises(ValueError, match="negative generation"):
        clean_actuals(raw)


def test_clean_forecasts_drops_negative_horizon():
    """Verify clean_forecasts filters out rows with horizon_h <= 0."""
    raw = [
        # Future forecast: horizon = 2.0h -> keep
        {
            "publishTime": "2026-01-01T00:00:00Z",
            "startTime": "2026-01-01T02:00:00Z",
            "generation": 15000.0,
        },
        # Exactly zero horizon: horizon = 0.0h -> drop
        {
            "publishTime": "2026-01-01T00:00:00Z",
            "startTime": "2026-01-01T00:00:00Z",
            "generation": 14000.0,
        },
        # Back-cast: horizon = -2.0h -> drop
        {
            "publishTime": "2026-01-01T02:00:00Z",
            "startTime": "2026-01-01T00:00:00Z",
            "generation": 13000.0,
        },
    ]

    cleaned = clean_forecasts(raw)

    assert len(cleaned) == 1
    assert cleaned.iloc[0]["horizon_h"] == 2.0
    assert cleaned.iloc[0]["generation_mw"] == 15000.0


def test_clean_forecasts_dedupes():
    """Verify clean_forecasts dedupes on (publish_time, start_time)."""
    raw = [
        {
            "publishTime": "2026-01-01T00:00:00Z",
            "startTime": "2026-01-01T06:00:00Z",
            "generation": 12000.0,
        },
        {
            "publishTime": "2026-01-01T00:00:00Z",
            "startTime": "2026-01-01T06:00:00Z",
            "generation": 12000.0,
        },
    ]

    cleaned = clean_forecasts(raw)
    assert len(cleaned) == 1
    assert cleaned.iloc[0]["horizon_h"] == 6.0


def test_clean_empty_records():
    """Verify clean functions return expected empty structures on empty input."""
    assert clean_actuals([]).empty
    assert list(clean_actuals([]).columns) == [
        "start_time",
        "generation_mw",
        "settlement_date",
        "settlement_period",
    ]
    assert clean_forecasts([]).empty
    assert list(clean_forecasts([]).columns) == [
        "publish_time",
        "start_time",
        "generation_mw",
        "horizon_h",
    ]
