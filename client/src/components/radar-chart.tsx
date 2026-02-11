import { Radar, RadarChart as RechartsRadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer } from 'recharts';
import type { RadarAxis } from '@/types';

interface RadarChartProps {
  data: RadarAxis[];
}

export function RadarChart({ data }: RadarChartProps) {
  return (
    <div className="h-80 w-full">
      <ResponsiveContainer>
        <RechartsRadarChart data={data} cx="50%" cy="50%" outerRadius="80%">
          <PolarGrid />
          <PolarAngleAxis dataKey="label" tick={{ fontSize: 12 }} />
          <PolarRadiusAxis domain={[0, 100]} tick={false} />
          <Radar name="Player" dataKey="value" stroke="hsl(var(--primary))" fill="hsl(var(--primary))" fillOpacity={0.2} strokeWidth={2} />
        </RechartsRadarChart>
      </ResponsiveContainer>
    </div>
  );
}
