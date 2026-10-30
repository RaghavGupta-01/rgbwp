"""Tests for core domain logic: cutoff, decision selection, and metrics."""

import pandas as pd

from app.core.time_utils import get_cutoff_timestamp
from app.services.decision import get_decision_forecast
from app.services.metrics import (
    aggregate_actuals_hourly,
    breakdown_by_hour,
    calculate_daily_metrics,
    calculate_summary_metrics,
)


def test_get_cutoff_timestamp():
    """Verify cutoff timestamp calculation for D-1 at 09:00 London/UTC."""
    # Delivery day 2026-01-02 -> Cutoff is 2026-01-01 09:00 UTC
    ts = get_cutoff_timestamp("2026-01-02", "09:00")
    assert ts == pd.Timestamp("2026-01-01 09:00:00+00:00")

    # Delivery day 2026-01-15 -> Cutoff is 2026-01-14 09:00 UTC
    ts2 = get_cutoff_timestamp("2026-01-15", "09:00")
    assert ts2 == pd.Timestamp("2026-01-14 09:00:00+00:00")


def test_get_decision_forecast_selection():
    """Verify pure function selects latest forecast published at or before cutoff."""
    target_hour = pd.Timestamp("2026-01-02 12:00:00+00:00")

    forecasts = pd.DataFrame(
        [
            # Version 1: early on D-1 (04:00) -> before cutoff
            {
                "publish_time": pd.Timestamp("2026-01-01 04:00:00+00:00"),
                "start_time": target_hour,
                "generation_mw": 10000.0,
                "horizon_h": 32.0,
            },
            # Version 2: just before cutoff on D-1 (08:30) -> should be selected
            {
                "publish_time": pd.Timestamp("2026-01-01 08:30:00+00:00"),
                "start_time": target_hour,
                "generation_mw": 11500.0,
                "horizon_h": 27.5,
            },
            # Version 3: after cutoff on D-1 (14:00) -> MUST be ignored
            {
                "publish_time": pd.Timestamp("2026-01-01 14:00:00+00:00"),
                "start_time": target_hour,
                "generation_mw": 13000.0,
                "horizon_h": 22.0,
            },
        ]
    )

    df_dec = get_decision_forecast(forecasts, "2026-01-02", "09:00")
    assert len(df_dec) == 24

    row = df_dec[df_dec["start_time"] == target_hour].iloc[0]
    assert row["generation_mw"] == 11500.0
    assert row["publish_time"] == pd.Timestamp("2026-01-01 08:30:00+00:00")
    assert not row["is_missing"]


def test_aggregate_actuals_hourly():
    """Verify half-hourly pairs are correctly averaged into hourly values."""
    actuals = pd.DataFrame(
        [
            {
                "start_time": pd.Timestamp("2026-01-02 00:00:00+00:00"),
                "generation_mw": 10000.0,
            },
            {
                "start_time": pd.Timestamp("2026-01-02 00:30:00+00:00"),
                "generation_mw": 12000.0,
            },
            {
                "start_time": pd.Timestamp("2026-01-02 01:00:00+00:00"),
                "generation_mw": 14000.0,
            },
            {
                "start_time": pd.Timestamp("2026-01-02 01:30:00+00:00"),
                "generation_mw": 16000.0,
            },
        ]
    )

    hourly = aggregate_actuals_hourly(actuals)
    assert len(hourly) == 2
    assert hourly.iloc[0]["actual_mw"] == 11000.0  # mean(10000, 12000)
    assert hourly.iloc[1]["actual_mw"] == 15000.0  # mean(14000, 16000)


def test_metrics_calculations():
    """Verify hand-computed error metrics match calculations."""
    # 4 hourly evaluation points
    eval_df = pd.DataFrame(
        [
            {
                "start_time": pd.Timestamp("2026-01-02 00:00:00+00:00"),
                "delivery_date": "2026-01-02",
                "hour_of_day": 0,
                "forecast_mw": 100.0,
                "actual_mw": 90.0,
                "error_mw": 10.0,  # over-forecast
                "abs_error_mw": 10.0,
            },
            {
                "start_time": pd.Timestamp("2026-01-02 01:00:00+00:00"),
                "delivery_date": "2026-01-02",
                "hour_of_day": 1,
                "forecast_mw": 100.0,
                "actual_mw": 120.0,
                "error_mw": -20.0,  # under-forecast
                "abs_error_mw": 20.0,
            },
            {
                "start_time": pd.Timestamp("2026-01-02 02:00:00+00:00"),
                "delivery_date": "2026-01-02",
                "hour_of_day": 2,
                "forecast_mw": 80.0,
                "actual_mw": 80.0,
                "error_mw": 0.0,
                "abs_error_mw": 0.0,
            },
            {
                "start_time": pd.Timestamp("2026-01-02 03:00:00+00:00"),
                "delivery_date": "2026-01-02",
                "hour_of_day": 3,
                "forecast_mw": 110.0,
                "actual_mw": 100.0,
                "error_mw": 10.0,
                "abs_error_mw": 10.0,
            },
        ]
    )

    metrics = calculate_summary_metrics(eval_df)

    # MAE = (10 + 20 + 0 + 10) / 4 = 10.0
    assert metrics["mae"] == 10.0
    # Bias = (10 - 20 + 0 + 10) / 4 = 0.0
    assert metrics["bias"] == 0.0
    # RMSE = sqrt((100 + 400 + 0 + 100) / 4) = sqrt(150) ~= 12.25
    assert metrics["rmse"] == 12.25
    # Mean actual = (90 + 120 + 80 + 100) / 4 = 97.5
    assert metrics["mean_actual"] == 97.5
    # Under-forecast count = 1 out of 4 (25%)
    assert metrics["under_forecast_share_pct"] == 25.0

    # Test daily and hourly breakdowns
    daily = calculate_daily_metrics(eval_df)
    assert len(daily) == 1
    assert daily[0]["mae"] == 10.0

    by_hour = breakdown_by_hour(eval_df)
    assert len(by_hour) == 4
