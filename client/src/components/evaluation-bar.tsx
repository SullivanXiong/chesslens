interface EvaluationBarProps {
  score: number; // centipawns from white's perspective
  height?: number;
}

export function EvaluationBar({ score, height = 400 }: EvaluationBarProps) {
  // Convert centipawn score to percentage (50% = equal, 100% = winning for white)
  const clampedScore = Math.max(-1000, Math.min(1000, score));
  const whitePercent = 50 + (clampedScore / 1000) * 50;

  const displayScore = Math.abs(score) >= 10000
    ? (score > 0 ? 'M' : '-M')
    : (score / 100).toFixed(1);

  return (
    <div className="flex flex-col items-center gap-1" style={{ height }}>
      <span className="text-xs font-mono">{displayScore}</span>
      <div className="flex-1 w-6 rounded overflow-hidden border relative">
        <div className="absolute inset-0 bg-gray-800" />
        <div
          className="absolute bottom-0 left-0 right-0 bg-white transition-all duration-300"
          style={{ height: `${whitePercent}%` }}
        />
      </div>
    </div>
  );
}
