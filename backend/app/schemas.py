"""Pydantic v2 schemas for API responses."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class MetaResponse(BaseModel):
    """Metadata describing system parameters and data coverage."""

    decision_date_from: str
    decision_date_to: str
    delivery_date_from: str
    delivery_date_to: str
    default_cutoff_time: str
    timezone: str
    error_convention: str = Field(
        default="error = forecast - actual (MW). "
        "Positive error (>0) indicates over-forecast; "
        "negative error (<0) indicates under-forecast."
    )
    actuals_row_count: int
    forecasts_row_count: int


class ForecastHourPoint(BaseModel):
    """Hourly forecast and actual comparison point."""

    start_time: str
    publish_time: Optional[str] = None
    forecast_mw: Optional[float] = None
    actual_mw: Optional[float] = None
    horizon_h: Optional[float] = None
    is_missing: bool
    band_lower_mw: Optional[float] = None
    band_upper_mw: Optional[float] = None


class DecisionForecastResponse(BaseModel):
    """Decision view payload for a delivery date."""

    delivery_date: str
    cutoff_time: str
    cutoff_ts_utc: str
    points: List[ForecastHourPoint]
    missing_hours_count: int
    kpis: Dict[str, Any]


class ForecastVersionRow(BaseModel):
    """Single forecast version row for revisions chart."""

    publish_time: str
    start_time: str
    generation_mw: float
    horizon_h: float


class ForecastVersionsResponse(BaseModel):
    """All published versions for target hours on a delivery day."""

    delivery_date: str
    versions: List[ForecastVersionRow]


class SummaryMetricsResponse(BaseModel):
    """Key quantitative accuracy metrics over an evaluation window."""

    n_hours: int
    mae: float
    rmse: float
    bias: float
    p50_abs_error: float
    p90_abs_error: float
    p95_abs_error: float
    signed_p10: float
    signed_p90: float
    mean_actual: float
    nmae_pct: float
    under_forecast_share_pct: float
    over_forecast_share_pct: float
