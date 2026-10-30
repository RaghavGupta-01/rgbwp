import React from 'react';
import ReactECharts from 'echarts-for-react';
import type { HourlyErrorRow } from '../../types/api';

interface ErrorHistogramProps {
  data: HourlyErrorRow[];
  signedP10: number;
  signedP90: number;
}

export const ErrorHistogram: React.FC<ErrorHistogramProps> = ({
  data,
  signedP10,
  signedP90,
}) => {
  // Compute histogram bins for signed error (forecast - actual)
  const errors = data.map((d) => d.error_mw);
  const binWidth = 500;
  const minVal = -6000;
  const maxVal = 6000;

  const binCounts: { [key: string]: number } = {};
  for (let b = minVal; b < maxVal; b += binWidth) {
    binCounts[`${b}`] = 0;
  }

  errors.forEach((err) => {
    const bucket = Math.floor(err / binWidth) * binWidth;
    if (bucket >= minVal && bucket < maxVal) {
      binCounts[`${bucket}`] = (binCounts[`${bucket}`] || 0) + 1;
    }
  });

  const categories = Object.keys(binCounts).map((b) => `${Number(b)} to ${Number(b) + binWidth}`);
  const counts = Object.values(binCounts);

  const option = {
    title: {
      text: 'Signed Error Distribution (Forecast − Actual)',
      subtext: `Empirical bounds: P10 = ${signedP10.toLocaleString()} MW (under), P90 = ${signedP90.toLocaleString()} MW (over).`,
      left: 10,
      textStyle: { fontSize: 14, fontWeight: 'bold', color: '#0f172a' },
      subtextStyle: { fontSize: 12, color: '#64748b' },
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: '{b}<br/><b>{c} hours</b>',
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '12%',
      top: '20%',
      containLabel: true,
    },
    xAxis: {
      type: 'category',
      data: categories,
      name: 'Error Bucket (MW)',
      axisLine: { lineStyle: { color: '#94a3b8' } },
      axisLabel: { color: '#475569', rotate: 45, interval: 1 },
    },
    yAxis: {
      type: 'value',
      name: 'Frequency (Hours)',
      splitLine: { lineStyle: { color: '#f1f5f9' } },
      axisLabel: { color: '#475569' },
    },
    series: [
      {
        name: 'Frequency',
        type: 'bar',
        data: counts,
        itemStyle: {
          color: (params: any) => {
            const idx = params.dataIndex;
            const startVal = minVal + idx * binWidth;
            return startVal >= 0 ? '#38bdf8' : '#818cf8';
          },
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
