import React from 'react';
import { Calendar, Clock, AlertCircle } from 'lucide-react';

interface ControlsBarProps {
  mode: 'decision' | 'accuracy';
  deliveryDate?: string;
  onDeliveryDateChange?: (date: string) => void;
  dateFrom?: string;
  onDateFromChange?: (date: string) => void;
  dateTo?: string;
  onDateToChange?: (date: string) => void;
  cutoffTime: string;
  onCutoffTimeChange: (cutoff: string) => void;
  minDate?: string;
  maxDate?: string;
}

export const ControlsBar: React.FC<ControlsBarProps> = ({
  mode,
  deliveryDate = '2026-01-02',
  onDeliveryDateChange,
  dateFrom = '2026-01-02',
  onDateFromChange,
  dateTo = '2026-02-01',
  onDateToChange,
  cutoffTime,
  onCutoffTimeChange,
  minDate = '2026-01-02',
  maxDate = '2026-02-01',
}) => {
  const commonCutoffs = ['07:00', '08:00', '09:00', '10:00', '11:00', '12:00'];

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-4 mb-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        {/* Left side: Date Selectors */}
        <div className="flex flex-wrap items-center gap-4">
          {mode === 'decision' ? (
            <div className="flex items-center space-x-2">
              <label htmlFor="delivery-date-input" className="text-xs font-semibold text-slate-500 uppercase tracking-wider flex items-center space-x-1">
                <Calendar className="w-3.5 h-3.5" />
                <span>Delivery Day</span>
              </label>
              <input
                id="delivery-date-input"
                type="date"
                value={deliveryDate}
                min={minDate}
                max={maxDate}
                onChange={(e) => onDeliveryDateChange?.(e.target.value)}
                className="bg-slate-50 border border-slate-300 text-slate-900 text-sm rounded-lg px-3 py-1.5 focus:ring-sky-500 focus:border-sky-500 font-medium"
              />
            </div>
          ) : (
            <div className="flex flex-wrap items-center gap-3">
              <div className="flex items-center space-x-2">
                <label htmlFor="from-date-input" className="text-xs font-semibold text-slate-500 uppercase tracking-wider flex items-center space-x-1">
                  <Calendar className="w-3.5 h-3.5" />
                  <span>From</span>
                </label>
                <input
                  id="from-date-input"
                  type="date"
                  value={dateFrom}
                  min={minDate}
                  max={maxDate}
                  onChange={(e) => onDateFromChange?.(e.target.value)}
                  className="bg-slate-50 border border-slate-300 text-slate-900 text-sm rounded-lg px-3 py-1.5 focus:ring-sky-500 focus:border-sky-500 font-medium"
                />
              </div>
              <div className="flex items-center space-x-2">
                <label htmlFor="to-date-input" className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                  To
                </label>
                <input
                  id="to-date-input"
                  type="date"
                  value={dateTo}
                  min={minDate}
                  max={maxDate}
                  onChange={(e) => onDateToChange?.(e.target.value)}
                  className="bg-slate-50 border border-slate-300 text-slate-900 text-sm rounded-lg px-3 py-1.5 focus:ring-sky-500 focus:border-sky-500 font-medium"
                />
              </div>
            </div>
          )}
        </div>

        {/* Right side: Cutoff selector */}
        <div className="flex items-center space-x-3">
          <label htmlFor="cutoff-time-select" className="text-xs font-semibold text-slate-500 uppercase tracking-wider flex items-center space-x-1">
            <Clock className="w-3.5 h-3.5" />
            <span>Decision Cutoff (D-1)</span>
          </label>
          <div className="relative">
            <select
              id="cutoff-time-select"
              value={cutoffTime}
              onChange={(e) => onCutoffTimeChange(e.target.value)}
              className="bg-slate-50 border border-slate-300 text-slate-900 text-sm rounded-lg px-3 py-1.5 pr-8 focus:ring-sky-500 focus:border-sky-500 font-medium cursor-pointer"
            >
              {commonCutoffs.map((time) => (
                <option key={time} value={time}>
                  {time} UK
                </option>
              ))}
            </select>
          </div>

          <div
            className="text-slate-400 hover:text-slate-600 cursor-help"
            title="Cutoff determines which forecast version is selected. The latest forecast published on D-1 at or before this time is evaluated."
          >
            <AlertCircle className="w-4 h-4" />
          </div>
        </div>
      </div>
    </div>
  );
};
