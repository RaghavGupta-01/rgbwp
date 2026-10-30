"""Forecast accuracy metrics, hourly actuals alignment, and error band calculations."""

from datetime import date
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd

from app.services.decision import get_decision_forecast


def aggregate_actuals_hourly(df_actuals: pd.DataFrame) -> pd.DataFrame:
    """Aggregate half-hourly actuals to hourly grid by taking the mean of pairs."""
    if df_actuals.empty:
        return pd.DataFrame(columns=["start_time", "actual_mw"])

    df = df_actuals.copy()
    # Floor to the beginning of the hour (e.g. 10:00 and 10:30 -> 10:00)
    df["hour_start"] = df["start_time"].dt.floor("1h")

    hourly = (
        df.groupby("hour_start")["generation_mw"]
        .agg(["mean", "count"])
        .reset_index()
    )
    # Only keep hours where we have data
    hourly = hourly.rename(
        columns={"hour_start": "start_time", "mean": "actual_mw"}
    )
    cols = ["start_time", "actual_mw"]
    return hourly[cols].sort_values("start_time").reset_index(drop=True)


def build_evaluation_grid(
    df_actuals: pd.DataFrame,
    df_forecasts: pd.DataFrame,
    date_from: date | str = "2026-01-02",
    date_to: date | str = "2026-02-01",
    cutoff_time_str: str = "09:00",
) -> pd.DataFrame:
    """Align decision forecasts and hourly actuals on hourly grid.

    Error convention: error = forecast - actual (MW)
      positive error (>0) = over-forecast (buyer under-procured other power)
      negative error (<0) = under-forecast (actual exceeds forecast)
    """
    start_d = (
        pd.Timestamp(date_from).date()
        if isinstance(date_from, str)
        else date_from
    )
    end_d = (
        pd.Timestamp(date_to).date()
        if isinstance(date_to, str)
        else date_to
    )

    hourly_actuals = aggregate_actuals_hourly(df_actuals)

    decision_frames: List[pd.DataFrame] = []
    curr_d = start_d
    while curr_d <= end_d:
        d_str = curr_d.strftime("%Y-%m-%d")
        df_dec = get_decision_forecast(df_forecasts, d_str, cutoff_time_str)
        decision_frames.append(df_dec)
        curr_d += pd.Timedelta(days=1)

    if not decision_frames:
        return pd.DataFrame()

    all_decision = pd.concat(decision_frames, ignore_index=True)

    # Merge on start_time
    merged = pd.merge(all_decision, hourly_actuals, on="start_time", how="inner")

    # Drop missing forecast hours for error calculation
    merged = merged[~merged["generation_mw"].isna()].copy()
    merged = merged.rename(columns={"generation_mw": "forecast_mw"})

    # Error calculation
    merged["error_mw"] = merged["forecast_mw"] - merged["actual_mw"]
    merged["abs_error_mw"] = merged["error_mw"].abs()
    merged["delivery_date"] = merged["start_time"].dt.strftime("%Y-%m-%d")
    merged["hour_of_day"] = merged["start_time"].dt.hour

    return merged.sort_values("start_time").reset_index(drop=True)


def calculate_summary_metrics(df_eval: pd.DataFrame) -> Dict[str, Any]:
    """Calculate key forecast accuracy KPIs across the evaluation grid."""
    if df_eval.empty:
        return {
            "n_hours": 0,
            "mae": 0.0,
            "rmse": 0.0,
            "bias": 0.0,
            "p50_abs_error": 0.0,
            "p90_abs_error": 0.0,
            "p95_abs_error": 0.0,
            "signed_p10": 0.0,
            "signed_p90": 0.0,
            "mean_actual": 0.0,
            "nmae_pct": 0.0,
            "under_forecast_share_pct": 0.0,
            "over_forecast_share_pct": 0.0,
        }

    errors = df_eval["error_mw"].to_numpy()
    abs_errors = df_eval["abs_error_mw"].to_numpy()
    actuals = df_eval["actual_mw"].to_numpy()

    mae = float(np.mean(abs_errors))
    rmse = float(np.sqrt(np.mean(errors**2)))
    bias = float(np.mean(errors))
    mean_actual = float(np.mean(actuals))

    nmae = (mae / mean_actual * 100.0) if mean_actual > 0 else 0.0

    p50_abs = float(np.percentile(abs_errors, 50))
    p90_abs = float(np.percentile(abs_errors, 90))
    p95_abs = float(np.percentile(abs_errors, 95))

    signed_p10 = float(np.percentile(errors, 10))
    signed_p90 = float(np.percentile(errors, 90))

    under_count = int(np.sum(errors < 0))
    total_count = len(errors)
    under_share = (under_count / total_count * 100.0) if total_count > 0 else 0.0
    over_share = 100.0 - under_share

    return {
        "n_hours": total_count,
        "mae": round(mae, 2),
        "rmse": round(rmse, 2),
        "bias": round(bias, 2),
        "p50_abs_error": round(p50_abs, 2),
        "p90_abs_error": round(p90_abs, 2),
        "p95_abs_error": round(p95_abs, 2),
        "signed_p10": round(signed_p10, 2),
        "signed_p90": round(signed_p90, 2),
        "mean_actual": round(mean_actual, 2),
        "nmae_pct": round(nmae, 2),
        "under_forecast_share_pct": round(under_share, 2),
        "over_forecast_share_pct": round(over_share, 2),
    }


def breakdown_by_hour(df_eval: pd.DataFrame) -> List[Dict[str, Any]]:
    """Compute MAE, RMSE, and Bias breakdown by hour of day (0..23)."""
    if df_eval.empty:
        return []

    grouped = (
        df_eval.groupby("hour_of_day")
        .apply(
            lambda g: pd.Series(
                {
                    "mae": round(float(g["abs_error_mw"].mean()), 2),
                    "bias": round(float(g["error_mw"].mean()), 2),
                    "rmse": round(float(np.sqrt((g["error_mw"] ** 2).mean())), 2),
                    "mean_actual": round(float(g["actual_mw"].mean()), 2),
                    "count": int(len(g)),
                }
            )
        )
        .reset_index()
    )
    return grouped.to_dict(orient="records")


def breakdown_by_generation_level(
    df_eval: pd.DataFrame,
    bins: Tuple[float, ...] = (0, 3000, 6000, 9000, 12000, 30000),
    labels: Tuple[str, ...] = (
        "0-3k MW",
        "3-6k MW",
        "6-9k MW",
        "9-12k MW",
        "12k+ MW",
    ),
) -> List[Dict[str, Any]]:
    """Compute error metrics grouped by generation level."""
    if df_eval.empty:
        return []

    df = df_eval.copy()
    df["level_bucket"] = pd.cut(
        df["actual_mw"], bins=list(bins), labels=list(labels), right=False
    )

    grouped = (
        df.groupby("level_bucket", observed=False)
        .apply(
            lambda g: pd.Series(
                {
                    "mae": round(float(g["abs_error_mw"].mean()), 2)
                    if len(g) > 0
                    else 0.0,
                    "bias": round(float(g["error_mw"].mean()), 2)
                    if len(g) > 0
                    else 0.0,
                    "rmse": round(float(np.sqrt((g["error_mw"] ** 2).mean())), 2)
                    if len(g) > 0
                    else 0.0,
                    "count": int(len(g)),
                }
            )
        )
        .reset_index()
    )
    grouped["level_bucket"] = grouped["level_bucket"].astype(str)
    return grouped.to_dict(orient="records")


def breakdown_by_horizon(
    df_actuals: pd.DataFrame,
    df_forecasts: pd.DataFrame,
    bins: Tuple[float, ...] = (0, 6, 12, 24, 36, 48, 100),
    labels: Tuple[str, ...] = (
        "0-6h",
        "6-12h",
        "12-24h",
        "24-36h",
        "36-48h",
        "48h+",
    ),
) -> List[Dict[str, Any]]:
    """Compute accuracy decay across lead time using all forecast versions."""
    if df_forecasts.empty or df_actuals.empty:
        return []

    hourly_actuals = aggregate_actuals_hourly(df_actuals)

    merged = pd.merge(df_forecasts, hourly_actuals, on="start_time", how="inner")
    if merged.empty:
        return []

    merged["error_mw"] = merged["generation_mw"] - merged["actual_mw"]
    merged["abs_error_mw"] = merged["error_mw"].abs()

    merged["horizon_bucket"] = pd.cut(
        merged["horizon_h"], bins=list(bins), labels=list(labels), right=False
    )

    grouped = (
        merged.groupby("horizon_bucket", observed=False)
        .apply(
            lambda g: pd.Series(
                {
                    "mae": round(float(g["abs_error_mw"].mean()), 2)
                    if len(g) > 0
                    else 0.0,
                    "bias": round(float(g["error_mw"].mean()), 2)
                    if len(g) > 0
                    else 0.0,
                    "rmse": round(float(np.sqrt((g["error_mw"] ** 2).mean())), 2)
                    if len(g) > 0
                    else 0.0,
                    "count": int(len(g)),
                }
            )
        )
        .reset_index()
    )
    grouped["horizon_bucket"] = grouped["horizon_bucket"].astype(str)
    return grouped.to_dict(orient="records")


def calculate_daily_metrics(df_eval: pd.DataFrame) -> List[Dict[str, Any]]:
    """Compute daily MAE and Bias for time series visualization."""
    if df_eval.empty:
        return []

    grouped = (
        df_eval.groupby("delivery_date")
        .apply(
            lambda g: pd.Series(
                {
                    "mae": round(float(g["abs_error_mw"].mean()), 2),
                    "bias": round(float(g["error_mw"].mean()), 2),
                    "rmse": round(float(np.sqrt((g["error_mw"] ** 2).mean())), 2),
                    "mean_actual": round(float(g["actual_mw"].mean()), 2),
                    "mean_forecast": round(float(g["forecast_mw"].mean()), 2),
                    "count": int(len(g)),
                }
            )
        )
        .reset_index()
    )
    return grouped.to_dict(orient="records")
