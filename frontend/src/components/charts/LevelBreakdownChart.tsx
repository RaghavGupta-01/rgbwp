import React from 'react';
import ReactECharts from 'echarts-for-react';
import type { LevelMetricRow } from '../../types/api';

interface LevelBreakdownChartProps {
  data: LevelMetricRow[];
}

export const LevelBreakdownChart: React.FC<LevelBreakdownChartProps> = ({ data }) => {
  const buckets = data.map((d) => d.level_bucket);
  const maes = data.map((d) => d.mae);
  const biases = data.map((d) => d.bias);

  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
    },
    legend: {
      data: ['MAE', 'Bias'],
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
      name: 'Actual Wind Level',
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
        name: 'Bias',
        type: 'bar',
        data: biases,
        itemStyle: { color: '#f59e0b' },
      },
    ],
  };

  return (
    <div className="bg-white p-5 rounded-xl shadow-sm border border-slate-200">
      <div className="mb-3">
        <h3 className="text-base font-bold text-slate-900">
          Error by Generation Level
        </h3>
      </div>
      <ReactECharts option={option} style={{ height: '340px', width: '100%' }} notMerge />
    </div>
  );
};
