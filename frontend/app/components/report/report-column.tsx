import { Link } from "react-router";
import { Globe, ExternalLink } from "lucide-react";
import { Badge } from "~/components/ui/badge";
import { relativeTime } from "~/lib/utils";
import { getSentimentConfig, SENTIMENT_BORDER } from "~/lib/constants";
import type { ResearchReport } from "~/types";
import type { ReactNode } from "react";

interface ReportColumnProps {
  title: string;
  icon: ReactNode;
  color: string;
  items: ResearchReport[];
}

const COLOR_BORDER: Record<string, string> = {
  blue: "border-blue-200 dark:border-blue-800/30",
  accent: "border-border/50",
  orange: "border-orange-200 dark:border-orange-800/30",
};

export function ReportColumn({ title, icon, color, items }: ReportColumnProps) {
  return (
    <div className="flex flex-col border border-border/50 rounded-xl overflow-hidden bg-card/30">
      <div className={`flex items-center gap-2 px-4 py-3 border-b ${COLOR_BORDER[color] || "border-border/50"} bg-muted/20 shrink-0`}>
        {icon}
        <h3 className="text-[11px] font-medium uppercase tracking-widest text-muted-foreground">{title}</h3>
        <Badge variant="outline" className="ml-auto text-[9px] font-mono">{items.length}</Badge>
      </div>
      <div className="flex flex-col divide-y divide-border/40 overflow-y-auto max-h-[60vh] lg:max-h-[480px]">
        {items.length === 0 && (
          <div className="py-12 text-center text-xs text-muted-foreground/40 italic">
            Chưa có báo cáo
          </div>
        )}
        {items.map(item => {
          const sent = getSentimentConfig(item.sentiment);
          const sourceUrl = item.original_source
            || item.source_citations?.[0]
            || item.sources?.[0];

          return (
            <div key={item.id} className="p-4 hover:bg-muted/20 motion-safe:transition-colors flex flex-col gap-2.5">
              <div className="flex items-center gap-2 flex-wrap">
                <span className={`inline-flex items-center gap-1 text-[10px] font-medium px-1.5 py-0.5 rounded-full border ${sent.cls}`}>
                  {sent.icon}{sent.label}
                </span>
                <span className="text-[10px] text-muted-foreground/50 tabular-nums ml-auto">
                  {relativeTime(item.created_at)}
                </span>
              </div>

              {sourceUrl ? (
                <a
                  href={sourceUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-[13px] font-medium text-foreground leading-snug hover:text-primary motion-safe:transition-colors line-clamp-2 flex items-start gap-1 group"
                >
                  <span>{item.title}</span>
                  <Globe className="w-3 h-3 text-muted-foreground/40 group-hover:text-primary shrink-0 mt-0.5 motion-safe:transition-colors" />
                </a>
              ) : (
                <p className="text-[13px] font-medium text-foreground/50 line-clamp-2 italic">
                  {item.title}
                  <span className="text-[10px] text-destructive/60 ml-1 font-normal">(thiếu nguồn)</span>
                </p>
              )}

              {(item.executive_summary || item.summary) && (
                <p className={`text-[11px] text-muted-foreground leading-relaxed line-clamp-3 border-l pl-2 ${SENTIMENT_BORDER[item.sentiment] || "border-border/50"}`}>
                  {item.executive_summary || item.summary}
                </p>
              )}

              <div className="flex items-center justify-between pt-0.5">
                {item.source_citations && item.source_citations.length > 0 ? (
                  <span className="text-[10px] text-muted-foreground/60 flex items-center gap-1">
                    <Globe className="w-3 h-3" />
                    {item.source_citations.length} nguồn dẫn chứng
                  </span>
                ) : sourceUrl ? (
                  <span className="text-[10px] text-muted-foreground/60 flex items-center gap-1">
                    <Globe className="w-3 h-3" />1 nguồn gốc
                  </span>
                ) : (
                  <span className="text-[10px] text-destructive/60">⚠ Chưa có dẫn chứng</span>
                )}
                <Link
                  to={`/reports/${item.id}`}
                  className="text-[10px] font-medium text-primary hover:underline flex items-center gap-0.5 uppercase tracking-wide"
                >
                  Phân tích <ExternalLink className="w-3 h-3" />
                </Link>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
