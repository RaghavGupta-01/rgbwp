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
    title: {
      text: 'Error by Generation Level',
      subtext: 'Analyzing accuracy and bias as actual wind generation increases.',
      left: 10,
      textStyle: { fontSize: 14, fontWeight: 'bold', color: '#0f172a' },
      subtextStyle: { fontSize: 12, color: '#64748b' },
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
    },
    legend: {
      data: ['MAE', 'Bias'],
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
      name: 'Actual Wind Level',
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
        name: 'Bias',
        type: 'bar',
        data: biases,
        itemStyle: { color: '#f59e0b' },
      },
    ],
  };

  return (
    <div className="bg-white p-4 rounded-xl shadow-sm border border-slate-200">
      <ReactECharts option={option} style={{ height: '340px', width: '100%' }} notMerge />
    </div>
  );
};
