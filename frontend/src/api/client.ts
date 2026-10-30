/**
 * Typed HTTP client wrapper for backend REST API.
 */

import type {
  DailyMetricRow,
  DecisionForecastResponse,
  ForecastVersionsResponse,
  HorizonMetricRow,
  HourlyErrorRow,
  HourMetricRow,
  LevelMetricRow,
  MetaResponse,
  SummaryMetricsResponse,
} from '../types/api';

const API_BASE = '/api';

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}

async function request<T>(endpoint: string, params?: Record<string, string>): Promise<T> {
  const url = new URL(endpoint, window.location.origin);
  if (params) {
    Object.entries(params).forEach(([key, val]) => {
      if (val !== undefined && val !== null) {
        url.searchParams.append(key, val);
      }
    });
  }

  const response = await fetch(url.toString(), {
    headers: {
      Accept: 'application/json',
    },
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new ApiError(response.status, errorText || `API error (${response.status})`);
  }

  return response.json() as Promise<T>;
}

export const apiClient = {
  getMeta: () => request<MetaResponse>(`${API_BASE}/meta`),

  getDecisionForecast: (date: string, cutoff: string) =>
    request<DecisionForecastResponse>(`${API_BASE}/forecasts/decision`, { date, cutoff }),

  getForecastVersions: (date: string) =>
    request<ForecastVersionsResponse>(`${API_BASE}/forecasts/versions`, { date }),

  getSummaryMetrics: (dateFrom: string, dateTo: string, cutoff: string) =>
    request<SummaryMetricsResponse>(`${API_BASE}/metrics/summary`, {
      date_from: dateFrom,
      date_to: dateTo,
      cutoff,
    }),

  getDailyMetrics: (dateFrom: string, dateTo: string, cutoff: string) =>
    request<DailyMetricRow[]>(`${API_BASE}/metrics/daily`, {
      date_from: dateFrom,
      date_to: dateTo,
      cutoff,
    }),

  getByHourMetrics: (dateFrom: string, dateTo: string, cutoff: string) =>
    request<HourMetricRow[]>(`${API_BASE}/metrics/by-hour`, {
      date_from: dateFrom,
      date_to: dateTo,
      cutoff,
    }),

  getByHorizonMetrics: () => request<HorizonMetricRow[]>(`${API_BASE}/metrics/by-horizon`),

  getByLevelMetrics: (dateFrom: string, dateTo: string, cutoff: string) =>
    request<LevelMetricRow[]>(`${API_BASE}/metrics/by-level`, {
      date_from: dateFrom,
      date_to: dateTo,
      cutoff,
    }),

  getHourlyErrors: (dateFrom: string, dateTo: string, cutoff: string) =>
    request<HourlyErrorRow[]>(`${API_BASE}/metrics/errors`, {
      date_from: dateFrom,
      date_to: dateTo,
      cutoff,
    }),
};
