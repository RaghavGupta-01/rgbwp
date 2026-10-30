import React from 'react';
import ReactECharts from 'echarts-for-react';
import type { DailyMetricRow } from '../../types/api';

interface DailyErrorChartProps {
  data: DailyMetricRow[];
}

export const DailyErrorChart: React.FC<DailyErrorChartProps> = ({ data }) => {
  const dates = data.map((d) => d.delivery_date.slice(5)); // 'MM-DD'
  const maes = data.map((d) => d.mae);
  const biases = data.map((d) => d.bias);

  const option = {
    title: {
      text: 'Daily Forecast Accuracy (MAE & Bias)',
      subtext: 'Tracking day-to-day error magnitude and directional procurement bias (MW).',
      left: 10,
      textStyle: { fontSize: 14, fontWeight: 'bold', color: '#0f172a' },
      subtextStyle: { fontSize: 12, color: '#64748b' },
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: (params: any) => {
        let res = `<div class="font-bold mb-1">${params[0].axisValue}</div>`;
        params.forEach((item: any) => {
          const val = `${Number(item.value).toLocaleString()} MW`;
          res += `<div style="display:flex; justify-content:space-between; gap:12px; margin-top:2px;">
                    <span style="color:${item.color}">${item.seriesName}:</span>
                    <span style="font-weight:600">${val}</span>
                  </div>`;
        });
        return res;
      },
    },
    legend: {
      data: ['Daily MAE', 'Signed Bias (Forecast - Actual)'],
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
      data: dates,
      axisLine: { lineStyle: { color: '#94a3b8' } },
      axisLabel: { color: '#475569', rotate: 45 },
    },
    yAxis: {
      type: 'value',
      name: 'Error (MW)',
      splitLine: { lineStyle: { color: '#f1f5f9' } },
      axisLabel: { color: '#475569', formatter: '{value} MW' },
    },
    series: [
      {
        name: 'Daily MAE',
        type: 'line',
        smooth: true,
        data: maes,
        lineStyle: { width: 3, color: '#0284c7' },
        itemStyle: { color: '#0284c7' },
      },
      {
        name: 'Signed Bias (Forecast - Actual)',
        type: 'bar',
        data: biases,
        itemStyle: {
          color: (params: any) => (params.value >= 0 ? '#f59e0b' : '#3b82f6'),
        },
      },
    ],
  };

  return (
    <div className="bg-white p-4 rounded-xl shadow-sm border border-slate-200">
      <ReactECharts option={option} style={{ height: '360px', width: '100%' }} notMerge />
    </div>
  );
};
