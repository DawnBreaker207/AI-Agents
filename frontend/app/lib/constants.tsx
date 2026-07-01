import { TrendingUp, TrendingDown, Minus } from "lucide-react";
import type { ReactNode } from "react";

// ── Sentiment ──

export interface SentimentConfig {
  label: string;
  icon: ReactNode;
  cls: string;
}

export const SENTIMENT_CONFIG: Record<string, SentimentConfig> = {
  POSITIVE: { label: "Tích cực", icon: <TrendingUp className="w-3 h-3" />, cls: "text-green-600 dark:text-green-400 bg-green-50 dark:bg-green-950/40 border-green-200 dark:border-green-800/40" },
  NEUTRAL:  { label: "Trung tính", icon: <Minus className="w-3 h-3" />, cls: "text-amber-600 dark:text-amber-400 bg-amber-50 dark:bg-amber-950/40 border-amber-200 dark:border-amber-800/40" },
  NEGATIVE: { label: "Tiêu cực", icon: <TrendingDown className="w-3 h-3" />, cls: "text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-950/40 border-red-200 dark:border-red-800/40" },
  "Tích cực": { label: "Tích cực", icon: <TrendingUp className="w-3 h-3" />, cls: "text-green-600 dark:text-green-400 bg-green-50 dark:bg-green-950/40" },
  "Trung tính":{ label: "Trung tính", icon: <Minus className="w-3 h-3" />, cls: "text-amber-600 dark:text-amber-400 bg-amber-50 dark:bg-amber-950/40" },
  "Tiêu cực": { label: "Tiêu cực", icon: <TrendingDown className="w-3 h-3" />, cls: "text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-950/40" },
};

export function getSentimentConfig(s: string): SentimentConfig {
  return SENTIMENT_CONFIG[s] ?? { label: s, icon: <Minus className="w-3 h-3" />, cls: "bg-muted text-muted-foreground" };
}

export const SENTIMENT_CLASSES: Record<string, string> = {
  POSITIVE: "text-green-700 dark:text-green-400 bg-green-50 dark:bg-green-950/40 border-green-200 dark:border-green-800/30",
  NEUTRAL:  "text-amber-700 dark:text-amber-400 bg-amber-50 dark:bg-amber-950/40 border-amber-200 dark:border-amber-800/30",
  NEGATIVE: "text-destructive bg-destructive/10 border-destructive/20",
  "Tích cực": "text-green-700 dark:text-green-400 bg-green-50 dark:bg-green-950/40 border-green-200 dark:border-green-800/30",
  "Trung tính": "text-amber-700 dark:text-amber-400 bg-amber-50 dark:bg-amber-950/40 border-amber-200 dark:border-amber-800/30",
  "Tiêu cực": "text-destructive bg-destructive/10 border-destructive/20",
};

// ── Categories ──

export const CATEGORY_STYLES: Record<string, string> = {
  AI_RESEARCH: "bg-purple-50 text-purple-700 dark:bg-purple-950 dark:text-purple-300",
  LAYOFF:      "bg-red-50 text-red-700 dark:bg-red-950 dark:text-red-300",
  VN_MARKET:   "bg-green-50 text-green-700 dark:bg-green-950 dark:text-green-300",
  DEV_TOOLS:   "bg-blue-50 text-blue-700 dark:bg-blue-950 dark:text-blue-300",
  SECURITY:    "bg-orange-50 text-orange-700 dark:bg-orange-950 dark:text-orange-300",
  BUSINESS:    "bg-amber-50 text-amber-700 dark:bg-amber-950 dark:text-amber-300",
  OTHER:       "bg-muted text-muted-foreground",
};

// ── Sentiment border colors ──

export const SENTIMENT_BORDER: Record<string, string> = {
  POSITIVE: "border-l-green-500",
  NEUTRAL: "border-l-amber-400",
  NEGATIVE: "border-l-red-500",
  "Tích cực": "border-l-green-500",
  "Trung tính": "border-l-amber-400",
  "Tiêu cực": "border-l-red-500",
};
