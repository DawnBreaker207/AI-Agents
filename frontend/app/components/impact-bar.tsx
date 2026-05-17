import { cn } from "~/lib/utils";
import type { NewsStatus } from "~/types";

interface ImpactBarProps {
  score:  number | null;
  status: NewsStatus;
}

const SEGMENT_COLOR: Record<NewsStatus, string> = {
  KEEP_URGENT: "bg-destructive",
  KEEP:        "bg-green-500",
  WATCH:       "bg-amber-400",
  PROCESSED:   "bg-blue-500",
  TRASH:       "bg-muted-foreground/30",
  PENDING:     "bg-muted-foreground/20",
};

export function ImpactBar({ score, status }: ImpactBarProps) {
  if (score === null) return null;

  // Chia 10 điểm thành 5 segment — mỗi segment = 2 điểm
  const filled = Math.min(5, Math.round((score / 10) * 5));
  const color  = SEGMENT_COLOR[status];

  return (
    <div className="flex items-center gap-1.5">
      <div className="flex items-center gap-0.5">
        {Array.from({ length: 5 }).map((_, i) => (
          <div
            key={i}
            className={cn(
              "w-3 h-1 rounded-full transition-colors",
              i < filled ? color : "bg-secondary"
            )}
          />
        ))}
      </div>
      <span className="text-[11px] text-muted-foreground font-medium tabular-nums">
        {score.toFixed(1)}
      </span>
    </div>
  );
}
