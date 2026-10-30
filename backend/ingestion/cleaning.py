"""Data cleaning and validation for Elexon actuals and forecasts."""

import logging
from typing import Any, Dict, List

import pandas as pd

logger = logging.getLogger(__name__)

MAX_PLAUSIBLE_GENERATION_MW = 30000.0


def clean_actuals(raw_records: List[Dict[str, Any]] | pd.DataFrame) -> pd.DataFrame:
    """Clean and validate half-hourly generation actuals."""
    if isinstance(raw_records, pd.DataFrame):
        df = raw_records.copy()
    else:
        df = pd.DataFrame(raw_records)

    if df.empty:
        return pd.DataFrame(
            columns=[
                "start_time",
                "generation_mw",
                "settlement_date",
                "settlement_period",
            ]
        )

    # Rename fields
    field_map = {
        "startTime": "start_time",
        "generation": "generation_mw",
        "settlementDate": "settlement_date",
        "settlementPeriod": "settlement_period",
    }
    df = df.rename(columns={k: v for k, v in field_map.items() if k in df.columns})

    # Timestamp conversion to tz-aware UTC
    df["start_time"] = pd.to_datetime(df["start_time"], utc=True)

    # Types
    df["generation_mw"] = pd.to_numeric(df["generation_mw"], errors="coerce")
    if "settlement_period" in df.columns:
        df["settlement_period"] = pd.to_numeric(
            df["settlement_period"], errors="coerce"
        ).astype("Int64")
    else:
        df["settlement_period"] = pd.NA

    if "settlement_date" not in df.columns:
        df["settlement_date"] = df["start_time"].dt.strftime("%Y-%m-%d")

    # Deduplicate on start_time and sort
    initial_count = len(df)
    df = df.drop_duplicates(subset=["start_time"]).sort_values("start_time")
    deduped_count = len(df)
    if initial_count != deduped_count:
        logger.info(
            "Deduped actuals: dropped %d duplicate records.",
            initial_count - deduped_count,
        )

    # Validation
    if df["start_time"].isna().any():
        raise ValueError("Actuals contain null start_time values.")
    if df["generation_mw"].isna().any():
        raise ValueError("Actuals contain null generation_mw values.")
    if (df["generation_mw"] < 0).any():
        raise ValueError("Actuals contain negative generation values.")

    high_gen = df[df["generation_mw"] > MAX_PLAUSIBLE_GENERATION_MW]
    if not high_gen.empty:
        logger.warning(
            "Found %d actuals rows exceeding plausible threshold of %s MW.",
            len(high_gen),
            MAX_PLAUSIBLE_GENERATION_MW,
        )

    output_cols = [
        "start_time",
        "generation_mw",
        "settlement_date",
        "settlement_period",
    ]
    return df[output_cols].reset_index(drop=True)


def clean_forecasts(
    raw_records: List[Dict[str, Any]] | pd.DataFrame,
) -> pd.DataFrame:
    """Clean and validate hourly wind generation forecasts."""
    if isinstance(raw_records, pd.DataFrame):
        df = raw_records.copy()
    else:
        df = pd.DataFrame(raw_records)

    if df.empty:
        return pd.DataFrame(
            columns=["publish_time", "start_time", "generation_mw", "horizon_h"]
        )

    # Rename fields
    field_map = {
        "publishTime": "publish_time",
        "startTime": "start_time",
        "generation": "generation_mw",
    }
    df = df.rename(columns={k: v for k, v in field_map.items() if k in df.columns})

    # Timestamp conversion to tz-aware UTC
    df["publish_time"] = pd.to_datetime(df["publish_time"], utc=True)
    df["start_time"] = pd.to_datetime(df["start_time"], utc=True)
    df["generation_mw"] = pd.to_numeric(df["generation_mw"], errors="coerce")

    # Calculate forecast horizon in hours
    df["horizon_h"] = (
        (df["start_time"] - df["publish_time"]).dt.total_seconds() / 3600.0
    )

    # Drop back-casts (horizon_h <= 0)
    initial_count = len(df)
    df = df[df["horizon_h"] > 0]
    dropped_backcasts = initial_count - len(df)
    if dropped_backcasts > 0:
        logger.info(
            "Dropped %d forecast rows with horizon <= 0 hours.", dropped_backcasts
        )

    # Deduplicate on (publish_time, start_time) and sort
    before_dedupe = len(df)
    df = df.drop_duplicates(subset=["publish_time", "start_time"]).sort_values(
        by=["publish_time", "start_time"]
    )
    if before_dedupe != len(df):
        logger.info(
            "Deduped forecasts: dropped %d duplicate records.",
            before_dedupe - len(df),
        )

    # Validation
    if df["publish_time"].isna().any():
        raise ValueError("Forecasts contain null publish_time values.")
    if df["start_time"].isna().any():
        raise ValueError("Forecasts contain null start_time values.")
    if df["generation_mw"].isna().any():
        raise ValueError("Forecasts contain null generation_mw values.")
    if (df["generation_mw"] < 0).any():
        raise ValueError("Forecasts contain negative generation values.")

    high_gen = df[df["generation_mw"] > MAX_PLAUSIBLE_GENERATION_MW]
    if not high_gen.empty:
        logger.warning(
            "Found %d forecast rows exceeding plausible threshold of %s MW.",
            len(high_gen),
            MAX_PLAUSIBLE_GENERATION_MW,
        )

    output_cols = ["publish_time", "start_time", "generation_mw", "horizon_h"]
    return df[output_cols].reset_index(drop=True)
