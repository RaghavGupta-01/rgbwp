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
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
    },
    legend: {
      data: ['MAE', 'RMSE'],
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
      data: buckets,
      name: 'Lead Time',
      axisLine: { lineStyle: { color: '#94a3b8' } },
      axisLabel: { color: '#475569' },
    },
    yAxis: {
      type: 'value',
      name: 'MW',
      nameTextStyle: {
        color: '#64748b',
        fontSize: 12,
        align: 'right',
        padding: [0, 8, 0, 0],
      },
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
    <div className="bg-white p-5 rounded-xl shadow-sm border border-slate-200">
      <div className="mb-3">
        <h3 className="text-base font-bold text-slate-900">
          Error vs Forecast Horizon (Lead Time Decay)
        </h3>
      </div>
      <ReactECharts option={option} style={{ height: '340px', width: '100%' }} notMerge />
    </div>
  );
};
