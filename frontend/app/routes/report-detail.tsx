import type { Route } from "./+types/report-detail";
import { getReportById } from "~/lib/api";
import { Link } from "react-router";
import { Badge } from "~/components/ui/badge";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { relativeTime } from "~/lib/utils";
import { ImpactBar } from "~/components/impact-bar";
import { ArrowLeft as ArrowLeftIcon, Globe as GlobeIcon, ExternalLink as ExternalLinkIcon } from "lucide-react";
import { cn } from "~/lib/utils";
import { SENTIMENT_CLASSES, CATEGORY_STYLES } from "~/lib/constants";

export const meta: Route.MetaFunction = ({ data }) => {
  const reportTitle = data?.report?.title || "Báo cáo chi tiết";
  return [
    { title: `${reportTitle} - TechScout Báo cáo` },
    { name: "description", content: `Báo cáo chiến lược chuyên sâu về công nghệ và tác động thị trường.` }
  ];
};

export async function loader({ params }: Route.LoaderArgs) {
  const report = await getReportById(Number(params.id));
  return { report };
}



export default function ReportDetail({ loaderData }: Route.ComponentProps) {
  const { report } = loaderData;

  const rawCategory = report.categories?.[0] || report.tags?.[0] || "OTHER";
  const categoryKey = rawCategory in CATEGORY_STYLES ? rawCategory : "OTHER";
  const categoryStyle = CATEGORY_STYLES[categoryKey];

  return (
    <div className="max-w-5xl mx-auto flex flex-col gap-8 animate-in fade-in duration-300 pb-16">
      
      {/* Back button */}
      <Link to="/reports" className="flex items-center gap-1.5 text-[13px] text-muted-foreground hover:text-foreground w-fit transition-colors">
        <ArrowLeftIcon className="w-3.5 h-3.5" />
        Quay lại báo cáo
      </Link>

      {/* Header */}
      <div className="flex flex-col gap-3">
        <div className="flex items-center gap-2 flex-wrap">
          <Badge className={cn("text-[10px] font-medium px-2 py-0 border-none rounded-full", categoryStyle)}>
            {rawCategory.replace("_", " ")}
          </Badge>
          <Badge variant="outline" className={cn("text-[10px] font-medium px-2 py-0 rounded-full", SENTIMENT_CLASSES[report.sentiment] || "bg-muted text-muted-foreground")}>
            {report.sentiment}
          </Badge>
        </div>

        <h1 className="text-lg font-medium text-foreground leading-snug">{report.title}</h1>

        {report.original_source && (
          <a 
            href={report.original_source} 
            target="_blank" 
            rel="noopener noreferrer" 
            className="inline-flex items-center gap-2 px-4 py-2 mt-2 bg-secondary/40 hover:bg-secondary text-secondary-foreground text-sm font-medium rounded-lg transition-colors w-fit border border-border/50"
          >
            <GlobeIcon className="w-4 h-4 text-primary" />
            Đọc bài báo gốc nguyên bản
            <ExternalLinkIcon className="w-3.5 h-3.5 opacity-50" />
          </a>
        )}

        <div className="flex items-center gap-3">
          <ImpactBar score={report.impact_score} status="PROCESSED" />
          <span className="text-muted-foreground/30">|</span>
          <span className="text-[11px] text-muted-foreground/60 tabular-nums">{relativeTime(report.created_at)}</span>
        </div>
      </div>

      {/* Sections — mỗi section có label nhỏ + content */}
      {[
        { label: "Tóm tắt điều hành",       content: report.executive_summary || report.summary },
        { label: "Phân tích kỹ thuật chuyên sâu",       content: report.technical_deep_dive },
        { label: "Tác động thị trường Việt Nam", content: report.vietnam_market_impact },
      ].map(({ label, content }) =>
        content ? (
          <div key={label} className="flex flex-col gap-2">
            <p className="text-[10px] font-medium uppercase tracking-widest text-muted-foreground/60">{label}</p>
            <div className="border border-border/50 rounded-lg px-4 py-3.5">
              {label === "Phân tích kỹ thuật chuyên sâu" ? (
                <div className="prose prose-sm dark:prose-invert max-w-none text-sm text-foreground leading-7">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {content}
                  </ReactMarkdown>
                </div>
              ) : (
                <p className="text-sm text-foreground leading-7">{content}</p>
              )}
            </div>
          </div>
        ) : null
      )}

      {/* Action items */}
      {report.strategic_action_items && report.strategic_action_items.length > 0 && (
        <div className="flex flex-col gap-2">
          <p className="text-[10px] font-medium uppercase tracking-widest text-muted-foreground/60">Hành động chiến lược</p>
          <div className="border border-border/50 rounded-lg divide-y divide-border/50 bg-background">
            {report.strategic_action_items.map((item, i) => (
              <div key={i} className="flex items-start gap-3 px-4 py-3">
                <span className="text-[11px] text-muted-foreground/40 tabular-nums mt-0.5">{String(i + 1).padStart(2, "0")}</span>
                <p className="text-[13px] text-foreground leading-relaxed">{item}</p>
              </div>
            ))}
          </div>
        </div>
      )}
      {/* Citations / Links */}
      {report.source_citations && report.source_citations.length > 0 && (
        <div className="flex flex-col gap-2 mt-4 pt-6 border-t border-border/50">
          <p className="text-[10px] font-medium uppercase tracking-widest text-muted-foreground/60">
            Nguồn gốc & Dẫn chứng (Đã xác minh)
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {report.source_citations.map((citation: string, idx: number) => (
              <a 
                key={idx}
                href={citation} 
                target="_blank" 
                rel="noopener noreferrer"
                className="flex items-center gap-3 p-3 border border-border/50 rounded-xl bg-card/30 hover:bg-secondary/40 transition-colors group"
              >
                <div className="p-2 bg-background rounded-lg border border-border/50 group-hover:scale-105 transition-transform">
                  <GlobeIcon className="w-4 h-4 text-primary" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-[10px] font-medium text-muted-foreground uppercase tracking-widest mb-0.5">Nguồn tham khảo {idx + 1}</p>
                  <p className="text-[13px] font-medium text-foreground group-hover:text-primary transition-colors truncate">
                    {citation.replace(/^https?:\/\//, '').replace(/^www\./, '')}
                  </p>
                </div>
                <ExternalLinkIcon className="w-4 h-4 text-muted-foreground shrink-0 opacity-40 group-hover:opacity-100 transition-opacity" />
              </a>
            ))}
          </div>
        </div>
      )}
      
    </div>
  );
}