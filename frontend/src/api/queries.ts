/**
 * TanStack Query hooks for backend API endpoints.
 */

import { useQuery } from '@tanstack/react-query';
import { apiClient } from './client';

export const queryKeys = {
  meta: ['meta'] as const,
  decisionForecast: (date: string, cutoff: string) => ['decisionForecast', date, cutoff] as const,
  forecastVersions: (date: string) => ['forecastVersions', date] as const,
  summaryMetrics: (dateFrom: string, dateTo: string, cutoff: string) =>
    ['summaryMetrics', dateFrom, dateTo, cutoff] as const,
  dailyMetrics: (dateFrom: string, dateTo: string, cutoff: string) =>
    ['dailyMetrics', dateFrom, dateTo, cutoff] as const,
  byHourMetrics: (dateFrom: string, dateTo: string, cutoff: string) =>
    ['byHourMetrics', dateFrom, dateTo, cutoff] as const,
  byHorizonMetrics: ['byHorizonMetrics'] as const,
  byLevelMetrics: (dateFrom: string, dateTo: string, cutoff: string) =>
    ['byLevelMetrics', dateFrom, dateTo, cutoff] as const,
  hourlyErrors: (dateFrom: string, dateTo: string, cutoff: string) =>
    ['hourlyErrors', dateFrom, dateTo, cutoff] as const,
};

export function useMeta() {
  return useQuery({
    queryKey: queryKeys.meta,
    queryFn: apiClient.getMeta,
    staleTime: Infinity,
  });
}

export function useDecisionForecast(date: string, cutoff: string) {
  return useQuery({
    queryKey: queryKeys.decisionForecast(date, cutoff),
    queryFn: () => apiClient.getDecisionForecast(date, cutoff),
    enabled: Boolean(date && cutoff),
  });
}

export function useForecastVersions(date: string) {
  return useQuery({
    queryKey: queryKeys.forecastVersions(date),
    queryFn: () => apiClient.getForecastVersions(date),
    enabled: Boolean(date),
  });
}

export function useSummaryMetrics(dateFrom: string, dateTo: string, cutoff: string) {
  return useQuery({
    queryKey: queryKeys.summaryMetrics(dateFrom, dateTo, cutoff),
    queryFn: () => apiClient.getSummaryMetrics(dateFrom, dateTo, cutoff),
    enabled: Boolean(dateFrom && dateTo && cutoff),
  });
}

export function useDailyMetrics(dateFrom: string, dateTo: string, cutoff: string) {
  return useQuery({
    queryKey: queryKeys.dailyMetrics(dateFrom, dateTo, cutoff),
    queryFn: () => apiClient.getDailyMetrics(dateFrom, dateTo, cutoff),
    enabled: Boolean(dateFrom && dateTo && cutoff),
  });
}

export function useByHourMetrics(dateFrom: string, dateTo: string, cutoff: string) {
  return useQuery({
    queryKey: queryKeys.byHourMetrics(dateFrom, dateTo, cutoff),
    queryFn: () => apiClient.getByHourMetrics(dateFrom, dateTo, cutoff),
    enabled: Boolean(dateFrom && dateTo && cutoff),
  });
}

export function useByHorizonMetrics() {
  return useQuery({
    queryKey: queryKeys.byHorizonMetrics,
    queryFn: apiClient.getByHorizonMetrics,
  });
}

export function useByLevelMetrics(dateFrom: string, dateTo: string, cutoff: string) {
  return useQuery({
    queryKey: queryKeys.byLevelMetrics(dateFrom, dateTo, cutoff),
    queryFn: () => apiClient.getByLevelMetrics(dateFrom, dateTo, cutoff),
    enabled: Boolean(dateFrom && dateTo && cutoff),
  });
}

export function useHourlyErrors(dateFrom: string, dateTo: string, cutoff: string) {
  return useQuery({
    queryKey: queryKeys.hourlyErrors(dateFrom, dateTo, cutoff),
    queryFn: () => apiClient.getHourlyErrors(dateFrom, dateTo, cutoff),
    enabled: Boolean(dateFrom && dateTo && cutoff),
  });
}
