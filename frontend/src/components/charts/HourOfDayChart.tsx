import React from 'react';
import ReactECharts from 'echarts-for-react';
import type { HourMetricRow } from '../../types/api';

interface HourOfDayChartProps {
  data: HourMetricRow[];
}

export const HourOfDayChart: React.FC<HourOfDayChartProps> = ({ data }) => {
  // Sort data by hour_of_day (0..23)
  const sorted = [...data].sort((a, b) => a.hour_of_day - b.hour_of_day);
  const hours = sorted.map((d) => `${String(d.hour_of_day).padStart(2, '0')}:00`);
  const maes = sorted.map((d) => d.mae);
  const biases = sorted.map((d) => d.bias);

  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: (params: Array<{ seriesName: string; value: number; name: string }>) => {
        if (!params || params.length === 0) return '';
        const hour = params[0].name;
        let html = `<div class="font-bold text-xs mb-1">${hour} Delivery Hour</div>`;
        for (const p of params) {
          const val = p.value;
          const sign = p.seriesName === 'Bias' && val > 0 ? '+' : '';
          html += `<div class="text-xs flex justify-between gap-4">
            <span class="text-slate-500">${p.seriesName}:</span>
            <span class="font-semibold">${sign}${val.toLocaleString()} MW</span>
          </div>`;
        }
        return html;
      },
    },
    legend: {
      data: ['MAE', 'Bias (Forecast − Actual)'],
      top: 0,
      right: 10,
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '8%',
      top: '40px',
      containLabel: true,
    },
    xAxis: {
      type: 'category',
      data: hours,
      name: 'Hour',
      axisLine: { lineStyle: { color: '#94a3b8' } },
      axisLabel: { color: '#475569', interval: 1 },
    },
    yAxis: {
      type: 'value',
      name: 'MW',
      splitLine: { lineStyle: { color: '#f1f5f9' } },
      axisLabel: { color: '#475569', formatter: '{value} MW' },
    },
    series: [
      {
        name: 'MAE',
        type: 'bar',
        data: maes,
        itemStyle: { color: '#0284c7', borderRadius: [3, 3, 0, 0] },
      },
      {
        name: 'Bias (Forecast − Actual)',
        type: 'line',
        data: biases,
        itemStyle: { color: '#f59e0b' },
        lineStyle: { width: 2.5 },
        symbol: 'circle',
        symbolSize: 6,
        markLine: {
          data: [{ yAxis: 0, lineStyle: { color: '#94a3b8', type: 'dashed' } }],
          symbol: 'none',
        },
      },
    ],
  };

  return (
    <div className="bg-white p-5 rounded-xl shadow-sm border border-slate-200">
      <div className="mb-3">
        <h3 className="text-base font-bold text-slate-900">
          Error & Bias by Hour of Day
        </h3>
      </div>
      <ReactECharts option={option} style={{ height: '340px', width: '100%' }} notMerge />
    </div>
  );
};
