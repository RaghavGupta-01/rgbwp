import React from 'react';
import ReactECharts from 'echarts-for-react';
import type { ForecastHourPoint } from '../../types/api';

interface DecisionChartProps {
  points: ForecastHourPoint[];
  cutoffTime: string;
  deliveryDate: string;
}

export const DecisionChart: React.FC<DecisionChartProps> = ({
  points,
  cutoffTime,
  deliveryDate,
}) => {
  const hours = points.map((p) => {
    const d = new Date(p.start_time);
    return `${d.getUTCHours().toString().padStart(2, '0')}:00`;
  });

  const forecastData = points.map((p) => p.forecast_mw ?? null);
  const actualData = points.map((p) => p.actual_mw ?? null);
  const bandLower = points.map((p) => p.band_lower_mw ?? null);
  const bandUpperDiff = points.map((p) => {
    if (p.band_upper_mw !== null && p.band_lower_mw !== null) {
      return Math.max(0, p.band_upper_mw - p.band_lower_mw);
    }
    return null;
  });

  const option = {
    title: {
      text: `Decision-Time Wind Forecast vs Actuals (${deliveryDate})`,
      subtext: `Cutoff: ${cutoffTime} UK on D-1. Shaded area represents empirical P10-P90 uncertainty band.`,
      left: 10,
      textStyle: { fontSize: 15, fontWeight: 'bold', color: '#0f172a' },
      subtextStyle: { fontSize: 12, color: '#64748b' },
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' },
      formatter: (params: any) => {
        let res = `<div class="font-bold mb-1">${deliveryDate} ${params[0].axisValue} UTC</div>`;
        params.forEach((item: any) => {
          if (item.seriesName === 'Lower Band') return;
          const val = item.value !== null && item.value !== undefined ? `${Number(item.value).toLocaleString()} MW` : 'N/A';
          res += `<div style="display:flex; justify-content:space-between; gap:12px; margin-top:2px;">
                    <span style="color:${item.color}">${item.seriesName}:</span>
                    <span style="font-weight:600">${val}</span>
                  </div>`;
        });
        return res;
      },
    },
    legend: {
      data: ['Decision Forecast', 'Outturn Actuals', 'P10-P90 Uncertainty Band'],
      top: 35,
      right: 20,
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '8%',
      top: '18%',
      containLabel: true,
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: hours,
      name: 'Hour (UTC)',
      axisLine: { lineStyle: { color: '#94a3b8' } },
      axisLabel: { color: '#475569' },
    },
    yAxis: {
      type: 'value',
      name: 'Generation (MW)',
      axisLine: { lineStyle: { color: '#94a3b8' } },
      splitLine: { lineStyle: { color: '#f1f5f9' } },
      axisLabel: { color: '#475569', formatter: '{value} MW' },
    },
    series: [
      // Base line for lower error band (transparent)
      {
        name: 'Lower Band',
        type: 'line',
        data: bandLower,
        lineStyle: { opacity: 0 },
        stack: 'confidence-band',
        symbol: 'none',
      },
      // Stacked band on top of lower to create area
      {
        name: 'P10-P90 Uncertainty Band',
        type: 'line',
        data: bandUpperDiff,
        lineStyle: { opacity: 0 },
        areaStyle: {
          color: 'rgba(14, 165, 233, 0.15)',
        },
        stack: 'confidence-band',
        symbol: 'none',
      },
      // Decision-time forecast curve
      {
        name: 'Decision Forecast',
        type: 'line',
        data: forecastData,
        smooth: true,
        lineStyle: {
          width: 3,
          color: '#0284c7',
        },
        itemStyle: {
          color: '#0284c7',
        },
      },
      // Actuals overlay
      {
        name: 'Outturn Actuals',
        type: 'line',
        data: actualData,
        smooth: true,
        lineStyle: {
          width: 2.5,
          color: '#10b981',
          type: 'solid',
        },
        itemStyle: {
          color: '#10b981',
        },
      },
    ],
  };

  return (
    <div className="bg-white p-4 rounded-xl shadow-sm border border-slate-200">
      <ReactECharts option={option} style={{ height: '420px', width: '100%' }} notMerge />
    </div>
  );
};
