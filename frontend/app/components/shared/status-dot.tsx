import { cn } from "~/lib/utils";
import type { NewsStatus } from "~/types";

const STATUS_COLORS: Record<NewsStatus, string> = {
  KEEP_URGENT: "bg-destructive",
  KEEP:        "bg-green-500",
  WATCH:       "bg-amber-500",
  TRASH:       "bg-muted-foreground/40",
  PROCESSED:   "bg-blue-500",
  PENDING:     "bg-muted-foreground/20",
};

interface StatusDotProps {
  status: NewsStatus;
  className?: string;
}

export function StatusDot({ status, className }: StatusDotProps) {
  return (
    <div className={cn("h-2 w-2 rounded-full", STATUS_COLORS[status], className)} />
  );
}
