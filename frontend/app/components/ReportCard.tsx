import { useState } from "react";
import { Link } from "react-router";
import type { ResearchReport } from "~/types";
import { Badge } from "~/components/ui/badge";
import { Button } from "~/components/ui/button";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "~/components/ui/collapsible";
import { relativeTime } from "~/lib/utils";
import { ImpactBar } from "~/components/impact-bar";
import { Globe as GlobeIcon, ChevronDown, ChevronUp, CheckSquare, Eye } from "lucide-react";
import { cn } from "~/lib/utils";
import { SENTIMENT_CLASSES, CATEGORY_STYLES } from "~/lib/constants";

export function ReportCard({ report }: { report: ResearchReport }) {
  const [isSummaryExpanded, setIsSummaryExpanded] = useState(false);
  const [isImpactExpanded, setIsImpactExpanded] = useState(false);
  const [isActionsOpen, setIsActionsOpen] = useState(false);

  const fullSummary = report.executive_summary || report.summary || "Chi tiết đang được tổng hợp.";
  const summaryLength = fullSummary.length;
  const displaySummary = isSummaryExpanded ? fullSummary : `${fullSummary.slice(0, 200)}${summaryLength > 200 ? "..." : ""}`;

  const fullImpact = report.vietnam_market_impact || "Đang phân tích đánh giá tác động.";
  const impactLength = fullImpact.length;
  const displayImpact = isImpactExpanded ? fullImpact : `${fullImpact.slice(0, 150)}${impactLength > 150 ? "..." : ""}`;

  const actions = report.strategic_action_items || [];
  const hasActions = actions.length > 0;
  const displayedActions = isActionsOpen ? actions : actions.slice(0, 3);

  // Derive categories or tags safely
  const rawCategory = report.categories?.[0] || report.tags?.[0] || "OTHER";
  const categoryKey = rawCategory in CATEGORY_STYLES ? rawCategory : "OTHER";
  const categoryStyle = CATEGORY_STYLES[categoryKey];

  return (
    <div className="flex flex-col bg-background border border-border/50 rounded-lg hover:border-border transition-colors overflow-hidden">
      <div className="px-4 py-3 flex flex-col gap-2 shrink-0 border-b border-border/30">
        <div className="flex items-center justify-between gap-2">
          <div className="flex flex-wrap gap-1.5">
            <Badge className={cn("text-[10px] font-medium px-2 py-0 border-none rounded-full", categoryStyle)}>
              {rawCategory.replace("_", " ")}
            </Badge>
            <Badge variant="outline" className={cn("text-[10px] font-medium px-2 py-0 rounded-full", SENTIMENT_CLASSES[report.sentiment] || "bg-muted text-muted-foreground")}>
              {report.sentiment}
            </Badge>
          </div>
          <span className="text-[11px] text-muted-foreground/60 tabular-nums">
            {relativeTime(report.created_at)}
          </span>
        </div>

        <h3 className="text-[13px] font-medium text-foreground leading-snug">
          {report.original_source ? (
            <a 
              href={report.original_source} 
              target="_blank" 
              rel="noopener noreferrer" 
              className="hover:underline inline-flex items-center gap-1 hover:text-primary transition-colors"
            >
              {report.title}
              <GlobeIcon className="w-3.5 h-3.5 text-muted-foreground/40 shrink-0" />
            </a>
          ) : (
            <span className="text-foreground/50 italic">
              {report.title}
              <span className="text-[10px] text-destructive/60 ml-1 font-normal not-italic">(chưa có link nguồn)</span>
            </span>
          )}
        </h3>

        {(report.source_citations && report.source_citations.length > 0) ? (
          <div className="flex items-center gap-1.5">
            <span className="inline-flex items-center gap-1 text-[10px] font-medium text-green-700 dark:text-green-400 bg-green-50 dark:bg-green-950/40 border border-green-200 dark:border-green-800/30 rounded-full px-2 py-0.5">
              <GlobeIcon className="w-2.5 h-2.5" />
              {report.source_citations.length} nguồn dẫn chứng đã xác minh
            </span>
          </div>
        ) : report.original_source ? (
          <div className="flex items-center gap-1.5">
            <span className="inline-flex items-center gap-1 text-[10px] font-medium text-blue-700 dark:text-blue-400 bg-blue-50 dark:bg-blue-950/40 border border-blue-200 dark:border-blue-800/30 rounded-full px-2 py-0.5">
              <GlobeIcon className="w-2.5 h-2.5" />
              1 nguồn gốc
            </span>
          </div>
        ) : (
          <div className="flex items-center gap-1.5">
            <span className="inline-flex items-center gap-1 text-[10px] font-medium text-destructive/70 bg-destructive/5 border border-destructive/20 rounded-full px-2 py-0.5">
              ⚠ Chưa có dẫn chứng
            </span>
          </div>
        )}
      </div>

      <div className="px-4 py-3.5 flex-1 flex flex-col gap-4 text-[12px]">
          <div className="flex flex-col gap-1">
          <span className="text-[10px] font-medium uppercase tracking-widest text-muted-foreground/60">Tóm tắt điều hành</span>
          <p className="leading-relaxed text-muted-foreground wrap-break-word">
            {displaySummary}
            {summaryLength > 200 && (
              <button 
                onClick={() => setIsSummaryExpanded(!isSummaryExpanded)} 
                className="text-primary font-medium ml-1.5 hover:underline uppercase text-[10px]"
              >
                {isSummaryExpanded ? "Thu gọn" : "Xem thêm"}
              </button>
            )}
          </p>
        </div>

        {report.vietnam_market_impact && (
          <div className="flex flex-col gap-1 bg-secondary/30 px-3 py-2.5 rounded-lg border border-border/30">
            <span className="text-[10px] font-medium uppercase tracking-widest text-primary flex items-center gap-1">
              <GlobeIcon className="w-3 h-3" /> Tác động thị trường Việt Nam
            </span>
            <p className="leading-relaxed text-foreground italic">
              &ldquo;{displayImpact}&rdquo;
              {impactLength > 150 && (
                <button 
                  onClick={() => setIsImpactExpanded(!isImpactExpanded)} 
                  className="text-primary font-medium ml-1.5 hover:underline uppercase text-[10px] not-italic"
                >
                  {isImpactExpanded ? "Thu gọn" : "Xem thêm"}
                </button>
              )}
            </p>
          </div>
        )}

        {hasActions && (
          <div className="flex flex-col gap-2">
            <span className="text-[10px] font-medium uppercase tracking-widest text-muted-foreground/60">Hành động chiến lược</span>
            <Collapsible open={isActionsOpen} onOpenChange={setIsActionsOpen} className="flex flex-col gap-1.5">
              <div className="flex flex-col gap-1.5">
                {displayedActions.map((action, index) => (
                  <div key={index} className="flex items-start gap-2 text-foreground">
                    <CheckSquare className="w-3.5 h-3.5 text-muted-foreground shrink-0 mt-0.5" />
                    <span className="leading-tight text-[12px]">{action}</span>
                  </div>
                ))}
              </div>

              {actions.length > 3 && (
                <CollapsibleContent className="space-y-1.5 pt-1.5">
                  {actions.slice(3).map((action, index) => (
                    <div key={index} className="flex items-start gap-2 text-foreground animate-in slide-in-from-top-1 duration-200">
                      <CheckSquare className="w-3.5 h-3.5 text-muted-foreground shrink-0 mt-0.5" />
                      <span className="leading-tight text-[12px]">{action}</span>
                    </div>
                  ))}
                </CollapsibleContent>
              )}

              {actions.length > 3 && (
                <CollapsibleTrigger asChild>
                  <Button variant="ghost" size="sm" className="h-6 w-full text-[10px] font-medium uppercase tracking-wider gap-1 hover:bg-secondary mt-1">
                    {isActionsOpen ? (
                      <>Thu gọn hành động <ChevronUp className="w-3 h-3" /></>
                    ) : (
                      <>Xem tất cả {actions.length} hành động <ChevronDown className="w-3 h-3" /></>
                    )}
                  </Button>
                </CollapsibleTrigger>
              )}
            </Collapsible>
          </div>
        )}

      </div>

      <div className="px-4 py-2.5 border-t border-border/40 bg-secondary/10 flex items-center justify-between shrink-0">
        <ImpactBar score={report.impact_score} status="PROCESSED" />
        <Button asChild variant="outline" size="sm" className="font-medium text-[11px] uppercase tracking-wider h-7 gap-1">
          <Link to={`/reports/${report.id}`}>
            <Eye className="w-3 h-3" /> Chi tiết
          </Link>
        </Button>
      </div>
      
    </div>
  );
}