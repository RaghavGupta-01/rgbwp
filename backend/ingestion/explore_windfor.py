"""Diagnostic utility for Elexon BMRS WINDFOR stream analysis."""

from datetime import datetime, timezone
from typing import Any, Dict, List

import httpx
import pandas as pd

API_URL = "https://data.elexon.co.uk/bmrs/api/v1/datasets/WINDFOR/stream"


def fetch_windfor_sample(
    publish_from: str = "2025-12-31T00:00:00Z",
    publish_to: str = "2026-01-03T00:00:00Z",
) -> List[Dict[str, Any]]:
    """Fetch sample WINDFOR stream from Elexon BMRS."""
    params = {
        "publishDateTimeFrom": publish_from,
        "publishDateTimeTo": publish_to,
    }
    headers = {"Accept": "application/json"}
    with httpx.Client(timeout=60.0) as client:
        response = client.get(API_URL, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        if isinstance(data, list):
            return data
        if isinstance(data, dict) and "data" in data:
            return data["data"]
        return []


def analyze_sample(rows: List[Dict[str, Any]]) -> None:
    """Analyze sample dataset and print statistical summary."""
    if not rows:
        print("No rows returned from Elexon WINDFOR API.")
        return

    df = pd.DataFrame(rows)
    print(f"Total rows fetched: {len(df)}")
    print(f"Columns present: {list(df.columns)}")

    col_map = {
        "publishTime": "publish_time",
        "startTime": "start_time",
        "generation": "generation_mw",
    }
    df = df.rename(columns=col_map)

    df["publish_time"] = pd.to_datetime(df["publish_time"], utc=True)
    df["start_time"] = pd.to_datetime(df["start_time"], utc=True)

    df["horizon_h"] = (
        (df["start_time"] - df["publish_time"]).dt.total_seconds() / 3600.0
    )

    print("\n--- Publish Time Summary ---")
    publish_summary = (
        df.groupby("publish_time")
        .agg(
            row_count=("start_time", "count"),
            min_start=("start_time", "min"),
            max_start=("start_time", "max"),
        )
        .reset_index()
    )
    print(f"Unique publish timestamps: {len(publish_summary)}")
    print("Sample publish times and start coverage:")
    print(publish_summary.head(10).to_string(index=False))

    if len(publish_summary) > 1:
        diffs = (
            publish_summary["publish_time"].diff().dt.total_seconds() / 3600.0
        ).dropna()
        print(
            f"\nCadence between publishes (hours): "
            f"min={diffs.min()}, median={diffs.median()}, max={diffs.max()}"
        )

    print("\n--- Horizon Distribution (hours) ---")
    print(df["horizon_h"].describe().to_string())

    invalid_horizon = df[df["horizon_h"] <= 0]
    print(
        f"\nRows with horizon <= 0 (unusable back-casts): {len(invalid_horizon)}"
    )
    if not invalid_horizon.empty:
        print(
            invalid_horizon[["publish_time", "start_time", "horizon_h"]]
            .head(5)
            .to_string(index=False)
        )

    print("\n--- Versions per Target Hour (start_time) ---")
    versions_per_hour = df.groupby("start_time")["publish_time"].nunique()
    print(versions_per_hour.describe().to_string())

    print("\n--- Generation Range (MW) ---")
    if "generation_mw" in df.columns:
        print(df["generation_mw"].describe().to_string())


if __name__ == "__main__":
    now_utc = datetime.now(timezone.utc).isoformat()
    print(f"[{now_utc}] Probing Elexon WINDFOR dataset...")
    raw_data = fetch_windfor_sample()
    analyze_sample(raw_data)
