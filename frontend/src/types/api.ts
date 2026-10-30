/**
 * TypeScript interfaces matching backend OpenAPI schemas.
 */

export interface MetaResponse {
  decision_date_from: string;
  decision_date_to: string;
  delivery_date_from: string;
  delivery_date_to: string;
  default_cutoff_time: string;
  timezone: string;
  error_convention: string;
  actuals_row_count: number;
  forecasts_row_count: number;
}

export interface ForecastHourPoint {
  start_time: string;
  publish_time: string | null;
  forecast_mw: number | null;
  actual_mw: number | null;
  horizon_h: number | null;
  is_missing: boolean;
  band_lower_mw: number | null;
  band_upper_mw: number | null;
}

export interface DecisionForecastKPIs {
  forecast_peak_mw: number;
  forecast_average_mw: number;
  forecast_min_mw: number;
  earliest_publish_time: string | null;
  latest_publish_time: string | null;
  min_horizon_h: number | null;
  max_horizon_h: number | null;
}

export interface DecisionForecastResponse {
  delivery_date: string;
  cutoff_time: string;
  cutoff_ts_utc: string;
  points: ForecastHourPoint[];
  missing_hours_count: number;
  kpis: DecisionForecastKPIs;
}

export interface ForecastVersionRow {
  publish_time: string;
  start_time: string;
  generation_mw: number;
  horizon_h: number;
}

export interface ForecastVersionsResponse {
  delivery_date: string;
  versions: ForecastVersionRow[];
}

export interface SummaryMetricsResponse {
  n_hours: number;
  mae: number;
  rmse: number;
  bias: number;
  p50_abs_error: number;
  p90_abs_error: number;
  p95_abs_error: number;
  signed_p10: number;
  signed_p90: number;
  mean_actual: number;
  nmae_pct: number;
  under_forecast_share_pct: number;
  over_forecast_share_pct: number;
}

export interface DailyMetricRow {
  delivery_date: string;
  mae: number;
  bias: number;
  rmse: number;
  mean_actual: number;
  mean_forecast: number;
  count: number;
}

export interface HourMetricRow {
  hour_of_day: number;
  mae: number;
  bias: number;
  rmse: number;
  mean_actual: number;
  count: number;
}

export interface HorizonMetricRow {
  horizon_bucket: string;
  mae: number;
  bias: number;
  rmse: number;
  count: number;
}

export interface LevelMetricRow {
  level_bucket: string;
  mae: number;
  bias: number;
  rmse: number;
  count: number;
}

export interface HourlyErrorRow {
  start_time: string;
  delivery_date: string;
  hour_of_day: number;
  forecast_mw: number;
  actual_mw: number;
  error_mw: number;
  abs_error_mw: number;
}
