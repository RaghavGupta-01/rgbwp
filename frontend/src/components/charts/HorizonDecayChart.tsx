import React from 'react';
import ReactECharts from 'echarts-for-react';
import type { HorizonMetricRow } from '../../types/api';

interface HorizonDecayChartProps {
  data: HorizonMetricRow[];
}

export const HorizonDecayChart: React.FC<HorizonDecayChartProps> = ({ data }) => {
  const buckets = data.map((d) => d.horizon_bucket);
  const maes = data.map((d) => d.mae);
  const rmses = data.map((d) => d.rmse);

  const option = {
    title: {
      text: 'Error vs Forecast Horizon (Lead Time Decay)',
      subtext: 'Quantifying accuracy loss as lead time increases before delivery.',
      left: 10,
      textStyle: { fontSize: 14, fontWeight: 'bold', color: '#0f172a' },
      subtextStyle: { fontSize: 12, color: '#64748b' },
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
    },
    legend: {
      data: ['MAE', 'RMSE'],
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
      data: buckets,
      name: 'Lead Time',
      axisLine: { lineStyle: { color: '#94a3b8' } },
      axisLabel: { color: '#475569' },
    },
    yAxis: {
      type: 'value',
      name: 'Error (MW)',
      splitLine: { lineStyle: { color: '#f1f5f9' } },
      axisLabel: { color: '#475569', formatter: '{value} MW' },
    },
    series: [
      {
        name: 'MAE',
        type: 'bar',
        data: maes,
        itemStyle: { color: '#0284c7' },
      },
      {
        name: 'RMSE',
        type: 'bar',
        data: rmses,
        itemStyle: { color: '#6366f1' },
      },
    ],
  };

  return (
    <div className="bg-white p-4 rounded-xl shadow-sm border border-slate-200">
      <ReactECharts option={option} style={{ height: '340px', width: '100%' }} notMerge />
    </div>
  );
};
