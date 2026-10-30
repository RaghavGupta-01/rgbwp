"""Decision-time forecast selection logic."""

from datetime import date

import pandas as pd

from app.core.time_utils import get_cutoff_timestamp


def get_decision_forecast(
    df_forecasts: pd.DataFrame,
    delivery_date: date | str,
    cutoff_time_str: str = "09:00",
) -> pd.DataFrame:
    """Pure domain function to select latest forecast before cutoff for delivery day D.

    For each target hour t on delivery day D (00:00 to 23:00 UTC):
    1. Filter forecasts where publish_time <= cutoff_ts and start_time == t.
    2. Pick the row with maximum publish_time.
    3. Return generation_mw, publish_time, horizon_h.
    4. If no forecast exists for hour t, generation_mw is NaN with is_missing=True.
    """
    if isinstance(delivery_date, str):
        delivery_d_str = delivery_date
    else:
        delivery_d_str = delivery_date.strftime("%Y-%m-%d")

    cutoff_ts = get_cutoff_timestamp(delivery_d_str, cutoff_time_str)

    # 24 target hours for delivery day D
    day_start = pd.Timestamp(f"{delivery_d_str} 00:00:00+00:00")
    day_end = pd.Timestamp(f"{delivery_d_str} 23:00:00+00:00")
    target_hours = pd.date_range(day_start, day_end, freq="1h")

    # Filter forecasts strictly published at or before cutoff and target on day D
    eligible = df_forecasts[
        (df_forecasts["publish_time"] <= cutoff_ts)
        & (df_forecasts["start_time"] >= day_start)
        & (df_forecasts["start_time"] <= day_end)
    ].copy()

    if eligible.empty:
        # Return 24 empty placeholder rows
        return pd.DataFrame(
            {
                "start_time": target_hours,
                "publish_time": [pd.NaT] * 24,
                "generation_mw": [float("nan")] * 24,
                "horizon_h": [float("nan")] * 24,
                "is_missing": [True] * 24,
                "cutoff_ts": [cutoff_ts] * 24,
            }
        )

    # For each start_time, pick latest publish_time
    # Sort ascending by publish_time, then drop duplicates keeping last
    latest = (
        eligible.sort_values(by="publish_time")
        .drop_duplicates(subset=["start_time"], keep="last")
        .copy()
    )

    # Reindex onto full 24-hour grid so missing hours are explicit
    full_grid = pd.DataFrame({"start_time": target_hours})
    merged = pd.merge(full_grid, latest, on="start_time", how="left")

    merged["is_missing"] = merged["generation_mw"].isna()
    merged["cutoff_ts"] = cutoff_ts

    output_cols = [
        "start_time",
        "publish_time",
        "generation_mw",
        "horizon_h",
        "is_missing",
        "cutoff_ts",
    ]
    return merged[output_cols].sort_values("start_time").reset_index(drop=True)


def get_all_day_versions(
    df_forecasts: pd.DataFrame,
    delivery_date: date | str,
) -> pd.DataFrame:
    """Return all forecast versions for delivery day D (for revisions chart)."""
    if isinstance(delivery_date, str):
        delivery_d_str = delivery_date
    else:
        delivery_d_str = delivery_date.strftime("%Y-%m-%d")

    day_start = pd.Timestamp(f"{delivery_d_str} 00:00:00+00:00")
    day_end = pd.Timestamp(f"{delivery_d_str} 23:00:00+00:00")

    day_versions = df_forecasts[
        (df_forecasts["start_time"] >= day_start)
        & (df_forecasts["start_time"] <= day_end)
    ].copy()

    return day_versions.sort_values(
        by=["publish_time", "start_time"]
    ).reset_index(drop=True)
