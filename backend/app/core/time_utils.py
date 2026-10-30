"""Timezone and cutoff computation utilities."""

import zoneinfo
from datetime import date, datetime, time

import pandas as pd


def get_cutoff_timestamp(
    delivery_date: date | str,
    cutoff_time_str: str = "09:00",
    tz_name: str = "Europe/London",
) -> pd.Timestamp:
    """Compute the UTC cutoff timestamp for a given delivery date (D)."""
    if isinstance(delivery_date, str):
        d_date = datetime.strptime(delivery_date, "%Y-%m-%d").date()
    else:
        d_date = delivery_date

    # Decision is made on D-1
    decision_date = d_date - pd.Timedelta(days=1)

    # Parse cutoff time
    c_time = time.fromisoformat(cutoff_time_str)

    tz = zoneinfo.ZoneInfo(tz_name)
    local_dt = datetime.combine(decision_date, c_time, tzinfo=tz)

    # Convert to UTC Timestamp
    return pd.Timestamp(local_dt).tz_convert("UTC")
