import { cn } from "~/lib/utils";
import type { NewsCategory } from "~/types";
import { Badge } from "~/components/ui/badge";
import { CATEGORY_STYLES } from "~/lib/constants";

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
