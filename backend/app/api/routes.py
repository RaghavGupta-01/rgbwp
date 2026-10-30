"""API endpoints for system metadata, forecasts, and accuracy metrics."""

from typing import Any, Dict, List

import pandas as pd
from fastapi import APIRouter, HTTPException, Query

from app.config import settings
from app.schemas import (
    DecisionForecastResponse,
    ForecastHourPoint,
    ForecastVersionRow,
    ForecastVersionsResponse,
    MetaResponse,
    SummaryMetricsResponse,
)
from app.services.data_store import data_store
from app.services.decision import get_all_day_versions, get_decision_forecast
from app.services.metrics import (
    aggregate_actuals_hourly,
    breakdown_by_generation_level,
    breakdown_by_horizon,
    breakdown_by_hour,
    build_evaluation_grid,
    calculate_daily_metrics,
    calculate_summary_metrics,
)

router = APIRouter(prefix="/api")


@router.get("/meta", response_model=MetaResponse, tags=["System"])
def get_metadata() -> MetaResponse:
    """Return data coverage, cutoff configuration, and data conventions."""
    df_act = data_store.actuals
    df_fc = data_store.forecasts

    return MetaResponse(
        decision_date_from=settings.DECISION_DATE_FROM,
        decision_date_to=settings.DECISION_DATE_TO,
        delivery_date_from=settings.DELIVERY_DATE_FROM,
        delivery_date_to=settings.DELIVERY_DATE_TO,
        default_cutoff_time=settings.DEFAULT_CUTOFF_TIME,
        timezone=settings.DEFAULT_TIMEZONE,
        actuals_row_count=len(df_act),
        forecasts_row_count=len(df_fc),
    )


@router.get(
    "/forecasts/decision",
    response_model=DecisionForecastResponse,
    tags=["Forecasts"],
)
def get_decision_view_data(
    date: str = Query(
        default="2026-01-02",
        description="Delivery date (YYYY-MM-DD)",
        examples=["2026-01-02"],
    ),
    cutoff: str = Query(
        default=settings.DEFAULT_CUTOFF_TIME,
        description="Cutoff time in Europe/London (HH:MM)",
        examples=["09:00"],
    ),
) -> DecisionForecastResponse:
    """Return decision forecast with empirical error band and actuals."""
    df_fc = data_store.forecasts
    df_act = data_store.actuals

    # Generate decision forecast for day D
    df_dec = get_decision_forecast(df_fc, date, cutoff)
    if df_dec.empty:
        raise HTTPException(
            status_code=404, detail=f"No forecast data available for {date}"
        )

    cutoff_ts_str = df_dec.iloc[0]["cutoff_ts"].isoformat()

    # Get hourly actuals for day D
    hourly_act = aggregate_actuals_hourly(df_act)
    merged = pd.merge(df_dec, hourly_act, on="start_time", how="left")

    # Compute empirical P10/P90 signed error band across January evaluation grid
    df_eval = build_evaluation_grid(
        df_act, df_fc, cutoff_time_str=cutoff
    )
    summary = calculate_summary_metrics(df_eval)
    p10_error = summary["signed_p10"]
    p90_error = summary["signed_p90"]

    points: List[ForecastHourPoint] = []
    for _, row in merged.iterrows():
        fc_val = (
            float(row["generation_mw"])
            if pd.notna(row["generation_mw"])
            else None
        )
        act_val = (
            float(row["actual_mw"]) if pd.notna(row["actual_mw"]) else None
        )
        pub_val = (
            row["publish_time"].isoformat()
            if pd.notna(row["publish_time"])
            else None
        )
        horiz_val = (
            float(row["horizon_h"]) if pd.notna(row["horizon_h"]) else None
        )

        # Empirical error band: forecast - P90 (lower) to forecast - P10 (upper)
        # error = forecast - actual => actual = forecast - error
        lower_band = (
            round(max(0.0, fc_val - p90_error), 2)
            if fc_val is not None
            else None
        )
        upper_band = (
            round(fc_val - p10_error, 2) if fc_val is not None else None
        )

        points.append(
            ForecastHourPoint(
                start_time=row["start_time"].isoformat(),
                publish_time=pub_val,
                forecast_mw=round(fc_val, 2) if fc_val is not None else None,
                actual_mw=round(act_val, 2) if act_val is not None else None,
                horizon_h=round(horiz_val, 2)
                if horiz_val is not None
                else None,
                is_missing=bool(row["is_missing"]),
                band_lower_mw=lower_band,
                band_upper_mw=upper_band,
            )
        )

    # Compute day KPIs
    valid_fc = [p.forecast_mw for p in points if p.forecast_mw is not None]
    kpis = {
        "forecast_peak_mw": max(valid_fc) if valid_fc else 0.0,
        "forecast_average_mw": round(sum(valid_fc) / len(valid_fc), 2)
        if valid_fc
        else 0.0,
        "forecast_min_mw": min(valid_fc) if valid_fc else 0.0,
        "earliest_publish_time": min(
            (p.publish_time for p in points if p.publish_time), default=None
        ),
        "latest_publish_time": max(
            (p.publish_time for p in points if p.publish_time), default=None
        ),
        "min_horizon_h": min(
            (p.horizon_h for p in points if p.horizon_h is not None),
            default=None,
        ),
        "max_horizon_h": max(
            (p.horizon_h for p in points if p.horizon_h is not None),
            default=None,
        ),
    }

    missing_count = sum(1 for p in points if p.is_missing)

    return DecisionForecastResponse(
        delivery_date=date,
        cutoff_time=cutoff,
        cutoff_ts_utc=cutoff_ts_str,
        points=points,
        missing_hours_count=missing_count,
        kpis=kpis,
    )


@router.get(
    "/forecasts/versions",
    response_model=ForecastVersionsResponse,
    tags=["Forecasts"],
)
def get_forecast_versions(
    date: str = Query(
        default="2026-01-02",
        description="Delivery date (YYYY-MM-DD)",
        examples=["2026-01-02"],
    ),
) -> ForecastVersionsResponse:
    """Return all published forecast versions targeting hours on delivery day D."""
    df_fc = data_store.forecasts
    df_versions = get_all_day_versions(df_fc, date)

    rows: List[ForecastVersionRow] = []
    for _, row in df_versions.iterrows():
        rows.append(
            ForecastVersionRow(
                publish_time=row["publish_time"].isoformat(),
                start_time=row["start_time"].isoformat(),
                generation_mw=round(float(row["generation_mw"]), 2),
                horizon_h=round(float(row["horizon_h"]), 2),
            )
        )

    return ForecastVersionsResponse(delivery_date=date, versions=rows)


@router.get(
    "/metrics/summary",
    response_model=SummaryMetricsResponse,
    tags=["Metrics"],
)
def get_metrics_summary(
    date_from: str = Query(default=settings.DELIVERY_DATE_FROM),
    date_to: str = Query(default=settings.DELIVERY_DATE_TO),
    cutoff: str = Query(default=settings.DEFAULT_CUTOFF_TIME),
) -> SummaryMetricsResponse:
    """Return summary KPIs (MAE, RMSE, Bias, P10/P90, nMAE) over date window."""
    df_eval = build_evaluation_grid(
        data_store.actuals,
        data_store.forecasts,
        date_from=date_from,
        date_to=date_to,
        cutoff_time_str=cutoff,
    )
    metrics = calculate_summary_metrics(df_eval)
    return SummaryMetricsResponse(**metrics)


@router.get("/metrics/daily", tags=["Metrics"])
def get_metrics_daily(
    date_from: str = Query(default=settings.DELIVERY_DATE_FROM),
    date_to: str = Query(default=settings.DELIVERY_DATE_TO),
    cutoff: str = Query(default=settings.DEFAULT_CUTOFF_TIME),
) -> List[Dict[str, Any]]:
    """Return daily error time series (MAE, Bias, RMSE) by delivery day."""
    df_eval = build_evaluation_grid(
        data_store.actuals,
        data_store.forecasts,
        date_from=date_from,
        date_to=date_to,
        cutoff_time_str=cutoff,
    )
    return calculate_daily_metrics(df_eval)


@router.get("/metrics/by-hour", tags=["Metrics"])
def get_metrics_by_hour(
    date_from: str = Query(default=settings.DELIVERY_DATE_FROM),
    date_to: str = Query(default=settings.DELIVERY_DATE_TO),
    cutoff: str = Query(default=settings.DEFAULT_CUTOFF_TIME),
) -> List[Dict[str, Any]]:
    """Return error metrics breakdown by hour of day (0..23)."""
    df_eval = build_evaluation_grid(
        data_store.actuals,
        data_store.forecasts,
        date_from=date_from,
        date_to=date_to,
        cutoff_time_str=cutoff,
    )
    return breakdown_by_hour(df_eval)


@router.get("/metrics/by-horizon", tags=["Metrics"])
def get_metrics_by_horizon() -> List[Dict[str, Any]]:
    """Return error metrics breakdown by forecast lead time horizon buckets."""
    return breakdown_by_horizon(data_store.actuals, data_store.forecasts)


@router.get("/metrics/by-level", tags=["Metrics"])
def get_metrics_by_level(
    date_from: str = Query(default=settings.DELIVERY_DATE_FROM),
    date_to: str = Query(default=settings.DELIVERY_DATE_TO),
    cutoff: str = Query(default=settings.DEFAULT_CUTOFF_TIME),
) -> List[Dict[str, Any]]:
    """Return error metrics breakdown by generation level buckets."""
    df_eval = build_evaluation_grid(
        data_store.actuals,
        data_store.forecasts,
        date_from=date_from,
        date_to=date_to,
        cutoff_time_str=cutoff,
    )
    return breakdown_by_generation_level(df_eval)


@router.get("/metrics/errors", tags=["Metrics"])
def get_hourly_errors(
    date_from: str = Query(default=settings.DELIVERY_DATE_FROM),
    date_to: str = Query(default=settings.DELIVERY_DATE_TO),
    cutoff: str = Query(default=settings.DEFAULT_CUTOFF_TIME),
) -> List[Dict[str, Any]]:
    """Return hourly error points for histogram and heatmap rendering."""
    df_eval = build_evaluation_grid(
        data_store.actuals,
        data_store.forecasts,
        date_from=date_from,
        date_to=date_to,
        cutoff_time_str=cutoff,
    )
    if df_eval.empty:
        return []

    cols = [
        "start_time",
        "delivery_date",
        "hour_of_day",
        "forecast_mw",
        "actual_mw",
        "error_mw",
        "abs_error_mw",
    ]
    df_clean = df_eval[cols].copy()
    df_clean["start_time"] = df_clean["start_time"].dt.strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )
    # Replace any NaNs
    df_clean = df_clean.fillna(0.0)
    return df_clean.to_dict(orient="records")
