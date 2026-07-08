import { Form } from "react-router";
import { cn } from "~/lib/utils";
import type { PendingNews, NewsStatus } from "~/types";
import { CategoryBadge } from "~/components/shared/category-badge";
import { relativeTime } from "~/lib/utils";
import { ImpactBar } from "~/components/shared/impact-bar";
import { Button } from "~/components/ui/button";
import { Globe as GlobeIcon } from "lucide-react";

interface NewsCardProps {
  news:         PendingNews;
  showPromote?: boolean;  // true ở Watch List, false ở Feed
  queuePos?:    number;   // hiện "Queue #N" nếu có giá trị
}

const ACCENT_COLOR: Record<NewsStatus, string> = {
  KEEP_URGENT: "bg-destructive",
  KEEP:        "bg-green-500",
  WATCH:       "bg-amber-400",
  PROCESSED:   "bg-blue-500",
  TRASH:       "bg-muted-foreground/20",
  PENDING:     "bg-border",
};

export function NewsCard({ news, showPromote = false, queuePos }: NewsCardProps) {
  return (
    <div className="relative bg-background border border-border/50 rounded-lg overflow-hidden hover:border-border transition-colors">
      {/* Accent bar — visual status indicator */}
      <div className={cn("absolute left-0 top-0 bottom-0 w-[3px]", ACCENT_COLOR[news.status])} />

      <div className="pl-4 pr-4 py-3.5 flex flex-col gap-2">

        {/* Tầng 1 — Meta: category badge + thời gian (nhỏ, muted) */}
        <div className="flex items-center gap-1.5 flex-wrap">
          {news.category && <CategoryBadge category={news.category} />}
          {news.published_at && (
            <>
              <span className="text-muted-foreground/40 mx-0.5">·</span>
              <span className="text-[11px] text-muted-foreground/60 tabular-nums">
                {relativeTime(news.published_at)}
              </span>
            </>
          )}
          {queuePos && (
            <>
              <span className="text-muted-foreground/40 mx-0.5">·</span>
              <span className="text-[11px] text-muted-foreground/60">
                Hàng đợi #{queuePos}
              </span>
            </>
          )}
        </div>

        {/* Tầng 2 — Title: anchor chính, font-medium, line-clamp-2 */}
        <a
          href={news.url}
          target="_blank"
          rel="noopener noreferrer"
          className="text-[13px] font-medium text-foreground leading-snug hover:underline underline-offset-2 line-clamp-2"
        >
          {news.title}
        </a>

        {/* Tầng 3 — Snippet: detail phụ, chỉ hiện khi có, line-clamp-2 */}
        {news.snippet && (
          <p className="text-[12px] text-muted-foreground leading-relaxed line-clamp-2">
            {news.snippet}
          </p>
        )}

        {/* Topic chips — tối đa 4 */}
        {news.matched_topics && news.matched_topics.length > 0 && (
          <div className="flex flex-wrap gap-1">
            {news.matched_topics.slice(0, 4).map((t) => (
              <span
                key={t}
                className="text-[10px] px-1.5 py-0.5 rounded-full bg-secondary text-muted-foreground border border-border/50"
              >
                {t}
              </span>
            ))}
          </div>
        )}

        {/* Footer — source + impact */}
        <div className="flex items-center justify-between pt-0.5">
          {/* Source */}
          <div className="flex items-center gap-1.5">
            <div className="w-3.5 h-3.5 rounded-[3px] bg-secondary flex items-center justify-center">
              <GlobeIcon className="w-2 h-2 text-muted-foreground/50" />
            </div>
            <span className="text-[11px] text-muted-foreground/60">
              {news.source_domain ?? "unknown"}
            </span>
          </div>

          {/* Impact bar */}
          <ImpactBar score={news.impact_score} status={news.status} />
        </div>

        {/* Promote button — chỉ hiện khi showPromote=true */}
        {showPromote && (
          <Form method="post">
            <input type="hidden" name="newsId" value={news.id} />
            <Button
              type="submit"
              variant="outline"
              size="sm"
              className="w-full text-[12px] h-7 mt-1"
            >
              Promote → Research
            </Button>
          </Form>
        )}
      </div>
    </div>
  );
}
