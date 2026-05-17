import { cn } from "~/lib/utils";
import type { NewsCategory } from "~/types";
import { Badge } from "~/components/ui/badge";

const CATEGORY_STYLES: Record<NewsCategory, string> = {
  AI_RESEARCH: "bg-purple-50 text-purple-700 dark:bg-purple-950 dark:text-purple-300",
  LAYOFF:      "bg-red-50 text-red-700 dark:bg-red-950 dark:text-red-300",
  VN_MARKET:   "bg-green-50 text-green-700 dark:bg-green-950 dark:text-green-300",
  DEV_TOOLS:   "bg-blue-50 text-blue-700 dark:bg-blue-950 dark:text-blue-300",
  SECURITY:    "bg-orange-50 text-orange-700 dark:bg-orange-950 dark:text-orange-300",
  BUSINESS:    "bg-amber-50 text-amber-700 dark:bg-amber-950 dark:text-amber-300",
  OTHER:       "bg-muted text-muted-foreground",
};

interface CategoryBadgeProps {
  category: NewsCategory;
  className?: string;
  children?: React.ReactNode;
}

export function CategoryBadge({ category, className, children }: CategoryBadgeProps) {
  return (
    <Badge variant="outline" className={cn(CATEGORY_STYLES[category], "border-none font-medium", className)}>
      {children || category}
    </Badge>
  );
}
