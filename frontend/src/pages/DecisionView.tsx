import React from 'react';
import {
  TrendingUp,
  Activity,
  ArrowDown,
  Clock,
  AlertTriangle,
} from 'lucide-react';
import { ControlsBar } from '../components/ControlsBar';
import { KpiCard } from '../components/KpiCard';
import { DecisionChart } from '../components/charts/DecisionChart';
import { RevisionsChart } from '../components/charts/RevisionsChart';
import { useDecisionForecast, useForecastVersions } from '../api/queries';

interface DecisionViewProps {
  deliveryDate: string;
  onDeliveryDateChange: (date: string) => void;
  cutoffTime: string;
  onCutoffTimeChange: (cutoff: string) => void;
}

export const DecisionView: React.FC<DecisionViewProps> = ({
  deliveryDate,
  onDeliveryDateChange,
  cutoffTime,
  onCutoffTimeChange,
}) => {
  const {
    data: decisionData,
    isLoading: isDecisionLoading,
    error: decisionError,
  } = useDecisionForecast(deliveryDate, cutoffTime);

  const {
    data: versionsData,
    isLoading: isVersionsLoading,
  } = useForecastVersions(deliveryDate);

  if (isDecisionLoading) {
    return (
      <div className="space-y-4 animate-pulse">
        <div className="h-16 bg-slate-200 rounded-xl"></div>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-28 bg-slate-200 rounded-xl"></div>
          ))}
        </div>
        <div className="h-96 bg-slate-200 rounded-xl"></div>
      </div>
    );
  }

  if (decisionError || !decisionData) {
    return (
      <div className="p-8 bg-rose-50 border border-rose-200 rounded-xl text-center text-rose-800">
        <AlertTriangle className="w-8 h-8 mx-auto text-rose-500 mb-2" />
        <h3 className="font-semibold text-lg">Unable to load decision forecast</h3>
        <p className="text-sm mt-1 text-rose-600">
          {(decisionError as Error)?.message || 'No forecast records found for this date.'}
        </p>
      </div>
    );
  }

  const { kpis, points, missing_hours_count } = decisionData;

  return (
    <div className="space-y-6">
      {/* Date & Cutoff Selector */}
      <ControlsBar
        mode="decision"
        deliveryDate={deliveryDate}
        onDeliveryDateChange={onDeliveryDateChange}
        cutoffTime={cutoffTime}
        onCutoffTimeChange={onCutoffTimeChange}
      />

      {/* Missing Hours Warning Banner */}
      {missing_hours_count > 0 && (
        <div className="p-4 bg-amber-50 border border-amber-200 rounded-xl flex items-center space-x-3 text-amber-800 text-sm">
          <AlertTriangle className="w-5 h-5 text-amber-600 shrink-0" />
          <div>
            <span className="font-semibold">{missing_hours_count} delivery hours</span> had no forecast published prior to the {cutoffTime} cutoff.
            These hours are flagged as missing on the decision curve.
          </div>
        </div>
      )}

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <KpiCard
          title="Forecast Peak"
          value={kpis.forecast_peak_mw}
          unit="MW"
          icon={TrendingUp}
          badge="Max Day Demand"
          badgeVariant="neutral"
          tooltip="Maximum expected wind generation during delivery day"
        />
        <KpiCard
          title="Daily Average"
          value={kpis.forecast_average_mw}
          unit="MW"
          icon={Activity}
          subtitle={`Min: ${kpis.forecast_min_mw.toLocaleString()} MW`}
          badgeVariant="neutral"
          tooltip="Average forecast wind generation across 24 delivery hours"
        />
        <KpiCard
          title="Forecast Minimum"
          value={kpis.forecast_min_mw}
          unit="MW"
          icon={ArrowDown}
          badge="Baseload"
          badgeVariant="neutral"
          tooltip="Lowest predicted wind generation level"
        />
        <KpiCard
          title="Decision Lead Time"
          value={kpis.min_horizon_h !== null ? `${kpis.min_horizon_h} - ${kpis.max_horizon_h}` : 'N/A'}
          unit="hours"
          icon={Clock}
          subtitle={
            kpis.latest_publish_time
              ? `Published: ${new Date(kpis.latest_publish_time).toISOString().slice(11, 16)} UTC`
              : 'Unknown'
          }
          badge="Before Cutoff"
          badgeVariant="success"
          tooltip="Lead time from publication to target delivery hour"
        />
      </div>

      {/* Main Decision Chart */}
      <DecisionChart
        points={points}
        cutoffTime={cutoffTime}
        deliveryDate={deliveryDate}
      />

      {/* Secondary Revisions Chart */}
      {!isVersionsLoading && versionsData && versionsData.versions.length > 0 && (
        <RevisionsChart
          versions={versionsData.versions}
          deliveryDate={deliveryDate}
        />
      )}
    </div>
  );
};
