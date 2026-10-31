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
    title: {
      text: 'Error & Bias by Hour of Day',
      subtext: 'Intraday profile of forecast error and directional bias across 24 delivery hours.',
      left: 10,
      textStyle: { fontSize: 14, fontWeight: 'bold', color: '#0f172a' },
      subtextStyle: { fontSize: 12, color: '#64748b' },
    },
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
      top: 35,
      right: 20,
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '8%',
      top: '20%',
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
    <div className="bg-white p-4 rounded-xl shadow-sm border border-slate-200">
      <ReactECharts option={option} style={{ height: '340px', width: '100%' }} notMerge />
    </div>
  );
};
