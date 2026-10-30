import React from 'react';
import ReactECharts from 'echarts-for-react';
import type { ForecastVersionRow } from '../../types/api';

interface RevisionsChartProps {
  versions: ForecastVersionRow[];
  deliveryDate: string;
}

export const RevisionsChart: React.FC<RevisionsChartProps> = ({
  versions,
  deliveryDate,
}) => {
  // Group versions by publish_time
  const versionsByPublish = new Map<string, ForecastVersionRow[]>();
  versions.forEach((row) => {
    const pub = row.publish_time;
    if (!versionsByPublish.has(pub)) {
      versionsByPublish.set(pub, []);
    }
    versionsByPublish.get(pub)!.push(row);
  });

  const hours = Array.from({ length: 24 }, (_, i) => `${i.toString().padStart(2, '0')}:00`);

  // Build series for up to the latest 8 published versions
  const sortedPublishes = Array.from(versionsByPublish.keys()).sort();
  const samplePublishes = sortedPublishes.slice(-8);

  const series = samplePublishes.map((pub, idx) => {
    const rows = versionsByPublish.get(pub)!;
    const rowMap = new Map(
      rows.map((r) => {
        const d = new Date(r.start_time);
        return [`${d.getUTCHours().toString().padStart(2, '0')}:00`, r.generation_mw];
      })
    );

    const isLatest = idx === samplePublishes.length - 1;
    const pubLabel = new Date(pub).toISOString().slice(5, 16).replace('T', ' ');

    return {
      name: `Pub: ${pubLabel}`,
      type: 'line',
      smooth: true,
      data: hours.map((h) => rowMap.get(h) ?? null),
      lineStyle: {
        width: isLatest ? 3 : 1.5,
        opacity: isLatest ? 1.0 : 0.6,
      },
    };
  });

  const option = {
    title: {
      text: `Forecast Evolution & Revisions (${deliveryDate})`,
      subtext: 'Revisions across publications showing forecast adjustments over lead time.',
      left: 10,
      textStyle: { fontSize: 14, fontWeight: 'bold', color: '#0f172a' },
      subtextStyle: { fontSize: 12, color: '#64748b' },
    },
    tooltip: {
      trigger: 'axis',
    },
    legend: {
      type: 'scroll',
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
      name: 'Hour (UTC)',
      axisLine: { lineStyle: { color: '#94a3b8' } },
      axisLabel: { color: '#475569' },
    },
    yAxis: {
      type: 'value',
      name: 'Generation (MW)',
      splitLine: { lineStyle: { color: '#f1f5f9' } },
      axisLabel: { color: '#475569', formatter: '{value} MW' },
    },
    series,
  };

  return (
    <div className="bg-white p-4 rounded-xl shadow-sm border border-slate-200 mt-6">
      <ReactECharts option={option} style={{ height: '360px', width: '100%' }} notMerge />
    </div>
  );
};
