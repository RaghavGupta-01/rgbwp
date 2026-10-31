import React from 'react';
import {
  Activity,
  AlertCircle,
  BarChart,
  Percent,
  Scale,
  ShieldCheck,
} from 'lucide-react';
import { ControlsBar } from '../components/ControlsBar';
import { KpiCard } from '../components/KpiCard';
import { DailyErrorChart } from '../components/charts/DailyErrorChart';
import { HourOfDayChart } from '../components/charts/HourOfDayChart';
import { HorizonDecayChart } from '../components/charts/HorizonDecayChart';
import { ErrorHistogram } from '../components/charts/ErrorHistogram';
import { LevelBreakdownChart } from '../components/charts/LevelBreakdownChart';
import {
  useByHorizonMetrics,
  useByHourMetrics,
  useByLevelMetrics,
  useDailyMetrics,
  useHourlyErrors,
  useSummaryMetrics,
} from '../api/queries';

interface AccuracyViewProps {
  dateFrom: string;
  onDateFromChange: (d: string) => void;
  dateTo: string;
  onDateToChange: (d: string) => void;
  cutoffTime: string;
  onCutoffTimeChange: (c: string) => void;
}

export const AccuracyView: React.FC<AccuracyViewProps> = ({
  dateFrom,
  onDateFromChange,
  dateTo,
  onDateToChange,
  cutoffTime,
  onCutoffTimeChange,
}) => {
  const {
    data: summary,
    isLoading: isSummaryLoading,
    error: summaryError,
    refetch: refetchSummary,
  } = useSummaryMetrics(dateFrom, dateTo, cutoffTime);

  const {
    data: dailyData,
    isLoading: isDailyLoading,
    error: dailyError,
    refetch: refetchDaily,
  } = useDailyMetrics(dateFrom, dateTo, cutoffTime);

  const {
    data: byHourData,
    isLoading: isByHourLoading,
    error: byHourError,
    refetch: refetchByHour,
  } = useByHourMetrics(dateFrom, dateTo, cutoffTime);

  const {
    data: horizonData,
    isLoading: isHorizonLoading,
    error: horizonError,
    refetch: refetchHorizon,
  } = useByHorizonMetrics();

  const {
    data: levelData,
    isLoading: isLevelLoading,
    error: levelError,
    refetch: refetchLevel,
  } = useByLevelMetrics(dateFrom, dateTo, cutoffTime);

  const {
    data: errorRows,
    isLoading: isErrorsLoading,
    error: errorsError,
    refetch: refetchErrors,
  } = useHourlyErrors(dateFrom, dateTo, cutoffTime);

  const isLoading =
    isSummaryLoading ||
    isDailyLoading ||
    isByHourLoading ||
    isHorizonLoading ||
    isLevelLoading ||
    isErrorsLoading;

  const hasError =
    Boolean(summaryError || dailyError || byHourError || horizonError || levelError || errorsError);

  const handleRetryAll = () => {
    refetchSummary();
    refetchDaily();
    refetchByHour();
    refetchHorizon();
    refetchLevel();
    refetchErrors();
  };

  if (isLoading) {
    return (
      <div className="space-y-4 animate-pulse">
        <div className="h-16 bg-slate-200 rounded-xl"></div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
          {[1, 2, 3, 4, 5].map((i) => (
            <div key={i} className="h-28 bg-slate-200 rounded-xl"></div>
          ))}
        </div>
        <div className="h-80 bg-slate-200 rounded-xl"></div>
      </div>
    );
  }

  if (hasError || !summary) {
    return (
      <div className="p-8 bg-rose-50 border border-rose-200 rounded-xl text-center text-rose-800">
        <AlertCircle className="w-8 h-8 mx-auto text-rose-500 mb-2" />
        <h3 className="font-semibold text-lg">Unable to load forecast accuracy metrics</h3>
        <p className="text-sm mt-1 text-rose-600">
          Failed to fetch accuracy evaluation data for the selected parameters.
        </p>
        <button
          type="button"
          onClick={handleRetryAll}
          className="mt-4 inline-flex items-center px-4 py-2 bg-rose-600 hover:bg-rose-700 text-white rounded-lg text-sm font-medium shadow-sm transition"
        >
          Retry
        </button>
      </div>
    );
  }

  // Derive plain-language procurement recommendation from summary numbers
  const biasLabel = summary.bias > 0 ? 'Over-forecast' : 'Under-forecast';
  const biasAdvice =
    summary.bias > 0
      ? `On average, wind forecast overshoots outturn by ${Math.abs(summary.bias)} MW. Buying team risks under-procuring from thermal/market sources if taking forecast raw.`
      : `On average, wind generation outturned ${Math.abs(summary.bias)} MW higher than forecast. System was long on wind.`;

  return (
    <div className="space-y-6">
      {/* Date Range & Cutoff Filter */}
      <ControlsBar
        mode="accuracy"
        dateFrom={dateFrom}
        onDateFromChange={onDateFromChange}
        dateTo={dateTo}
        onDateToChange={onDateToChange}
        cutoffTime={cutoffTime}
        onCutoffTimeChange={onCutoffTimeChange}
      />

      {/* Summary KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        <KpiCard
          title="MAE"
          value={summary.mae}
          unit="MW"
          icon={Activity}
          subtitle={`Normalized: ${summary.nmae_pct}%`}
          badge="Mean Abs Error"
          badgeVariant="neutral"
          tooltip="Mean Absolute Error across all evaluated delivery hours"
        />
        <KpiCard
          title="RMSE"
          value={summary.rmse}
          unit="MW"
          icon={BarChart}
          subtitle="Penalizes large errors"
          badge="Root Mean Sq"
          badgeVariant="neutral"
          tooltip="Root Mean Squared Error"
        />
        <KpiCard
          title="Overall Bias"
          value={`${summary.bias > 0 ? '+' : ''}${summary.bias}`}
          unit="MW"
          icon={Scale}
          subtitle={biasLabel}
          badge={summary.bias > 0 ? 'Buyer Short' : 'Buyer Long'}
          badgeVariant={summary.bias > 0 ? 'warning' : 'success'}
          tooltip="Average error (Forecast - Actual). Positive = Over-forecast"
        />
        <KpiCard
          title="P90 Abs Error"
          value={summary.p90_abs_error}
          unit="MW"
          icon={ShieldCheck}
          subtitle="90% of hours within this"
          badge="Tail Risk"
          badgeVariant="neutral"
          tooltip="90th percentile of absolute error"
        />
        <KpiCard
          title="Under-Forecast"
          value={`${summary.under_forecast_share_pct}%`}
          unit=""
          icon={Percent}
          subtitle={`Over: ${summary.over_forecast_share_pct}%`}
          badge={summary.under_forecast_share_pct > 50 ? 'Long Bias' : 'Short Bias'}
          badgeVariant="neutral"
          tooltip="Percentage of hours where actual wind exceeded forecast"
        />
      </div>

      {/* Actionable Buying Desk Panel */}
      <div className="bg-gradient-to-r from-sky-50 to-indigo-50 border border-sky-200 rounded-xl p-5 shadow-sm">
        <div className="flex items-start space-x-3">
          <div className="p-2 rounded-lg bg-sky-600 text-white shrink-0 mt-0.5">
            <AlertCircle className="w-5 h-5" />
          </div>
          <div>
            <h3 className="font-bold text-slate-900 text-base">
              Trading Desk Takeaway: Procurement Buffer Sizing
            </h3>
            <p className="text-sm text-slate-700 mt-1 leading-relaxed">
              {biasAdvice} At the 90th percentile, forecast deviated by up to{' '}
              <span className="font-bold text-sky-900">{summary.p90_abs_error.toLocaleString()} MW</span>.
              To cover 90% of delivery hours under forecast uncertainty, consider maintaining an asymmetric buffer
              between <span className="font-bold text-sky-900">{summary.signed_p10.toLocaleString()} MW</span> (downside)
              and <span className="font-bold text-sky-900">+{summary.signed_p90.toLocaleString()} MW</span> (upside).
            </p>
          </div>
        </div>
      </div>

      {/* Main Analytical Charts */}
      {dailyData && <DailyErrorChart data={dailyData} />}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {byHourData && <HourOfDayChart data={byHourData} />}
        {horizonData && <HorizonDecayChart data={horizonData} />}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {errorRows && (
          <ErrorHistogram
            data={errorRows}
            signedP10={summary.signed_p10}
            signedP90={summary.signed_p90}
          />
        )}
        {levelData && <LevelBreakdownChart data={levelData} />}
      </div>
    </div>
  );
};
