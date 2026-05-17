import { Link, useFetcher, useRevalidator } from "react-router";
import { Input } from "~/components/ui/input";
import { Button } from "~/components/ui/button";
import { ScrollArea } from "~/components/ui/scroll-area";
import { Badge } from "~/components/ui/badge";
import {
  Activity, Briefcase, Cpu, MessageSquare, Microscope,
  Send, X, TrendingUp, TrendingDown, Minus,
  ExternalLink, Globe, RefreshCcw, AlertTriangle,
  BarChart3, Zap, Clock
} from "lucide-react";
import { getStrategicReports, getReportHistory, chatWithAgent, getFeedMetrics, triggerPipeline, API_BASE_URL } from "~/lib/api";
import { useState, useEffect } from "react";
import type { Route } from "./+types/dashboard";
import type { ResearchReport, FeedMetrics } from "~/types";
import { relativeTime } from "~/lib/utils";
import JobWatchWidget from "~/components/JobWatchWidget";

export const meta: Route.MetaFunction = () => [
  { title: "Tổng quan thị trường - TechScout Intelligence" },
  { name: "description", content: "Bảng điều khiển thông tin thị trường công nghệ cá nhân được phân tích bởi AI." }
];

export async function loader({ request }: Route.LoaderArgs) {
  try {
    const [strategic, history, metrics] = await Promise.all([
      getStrategicReports(),
      getReportHistory(),
      getFeedMetrics(),
    ]);

    // Deduplicate and filter: chỉ giữ báo cáo có link gốc (nguyên tắc bắt buộc)
    const seen = new Set<number>();
    const allReports = [...strategic, ...history].filter(r => {
      const hasSource = (r.original_source && r.original_source.trim() !== "")
        || (r.source_citations && r.source_citations.length > 0);
      if (!hasSource || seen.has(r.id)) return false;
      seen.add(r.id);
      return true;
    });

    return { reports: allReports, metrics };
  } catch (err) {
    console.error("Dashboard loader failed:", err);
    return {
      reports: [],
      metrics: { total_today: 0, keep_urgent: 0, keep: 0, watch: 0, trash: 0, processed: 0, last_run_at: null }
    };
  }
}

export async function action({ request }: Route.ActionArgs) {
  const formData = await request.formData();
  const intent = formData.get("intent") as string;

  if (intent === "chat") {
    const prompt = formData.get("prompt") as string;
    try {
      const result = await chatWithAgent(prompt, "all");
      return { answer: result.answer };
    } catch {
      return { answer: "Agent protocol error: Không thể truy cập chatbot phân tích lúc này." };
    }
  }

  if (intent === "trigger") {
    try {
      await triggerPipeline();
      return { triggered: true };
    } catch {
      return { triggered: false };
    }
  }

  return {};
}

const SENTIMENT_CONFIG: Record<string, { label: string; icon: React.ReactNode; cls: string }> = {
  POSITIVE:   { label: "Tích cực", icon: <TrendingUp className="w-3 h-3" />,   cls: "text-green-600 dark:text-green-400 bg-green-50 dark:bg-green-950/40 border-green-200 dark:border-green-800/40" },
  NEUTRAL:    { label: "Trung tính", icon: <Minus className="w-3 h-3" />,       cls: "text-amber-600 dark:text-amber-400 bg-amber-50 dark:bg-amber-950/40 border-amber-200 dark:border-amber-800/40" },
  NEGATIVE:   { label: "Tiêu cực", icon: <TrendingDown className="w-3 h-3" />, cls: "text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-950/40 border-red-200 dark:border-red-800/40" },
  "Tích cực": { label: "Tích cực", icon: <TrendingUp className="w-3 h-3" />,   cls: "text-green-600 dark:text-green-400 bg-green-50 dark:bg-green-950/40" },
  "Trung tính":{ label: "Trung tính",icon: <Minus className="w-3 h-3" />,      cls: "text-amber-600 dark:text-amber-400 bg-amber-50 dark:bg-amber-950/40" },
  "Tiêu cực": { label: "Tiêu cực", icon: <TrendingDown className="w-3 h-3" />, cls: "text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-950/40" },
};

function getSentimentConfig(s: string) {
  return SENTIMENT_CONFIG[s] ?? { label: s, icon: <Minus className="w-3 h-3" />, cls: "bg-muted text-muted-foreground" };
}

export default function Dashboard({ loaderData }: Route.ComponentProps) {
  const { reports, metrics } = loaderData;
  const { revalidate, state } = useRevalidator();
  const [isAssistantOpen, setIsAssistantOpen] = useState(false);
  const [isTriggering, setIsTriggering] = useState(false);
  const [messages, setMessages] = useState<{ role: "ai" | "user"; text: string }[]>([
    { role: "ai", text: "Chào! Tôi đang giám sát luồng báo cáo thị trường. Bạn muốn tôi phân tích điều gì?" }
  ]);
  const chatFetcher = useFetcher<{ answer: string }>();

  // SSE Realtime
  useEffect(() => {
    const sse = new EventSource(`${API_BASE_URL}/api/news/stream`);
    sse.onmessage = (e) => {
      try {
        const data = JSON.parse(e.data);
        if (data.type === "new_news" && state === "idle") revalidate();
      } catch {}
    };
    return () => sse.close();
  }, [state, revalidate]);

  // Collect chat response
  useEffect(() => {
    if (chatFetcher.data?.answer) {
      setMessages(prev => [...prev, { role: "ai", text: chatFetcher.data!.answer }]);
    }
  }, [chatFetcher.data]);

  const handleTrigger = async () => {
    setIsTriggering(true);
    try {
      await triggerPipeline();
      revalidate();
    } finally {
      setIsTriggering(false);
    }
  };

  const handleChat = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const fd = new FormData(e.currentTarget);
    const prompt = fd.get("prompt") as string;
    if (!prompt.trim()) return;
    setMessages(prev => [...prev, { role: "user", text: prompt }]);
    chatFetcher.submit({ intent: "chat", prompt }, { method: "post" });
    e.currentTarget.reset();
  };

  // Route reports to columns
  const cols = { market: [] as ResearchReport[], jobs: [] as ResearchReport[], academic: [] as ResearchReport[], tech: [] as ResearchReport[] };
  for (const r of reports) {
    const txt = `${r.title} ${r.executive_summary ?? ""} ${(r.tags ?? []).join(" ")} ${(r.categories ?? []).join(" ")}`.toLowerCase();
    if (/job|layoff|salary|employment|hiring|tuy[eể]n|ngh[eề]/.test(txt)) cols.jobs.push(r);
    else if (/academic|research|paper|study|thesis|h[oọ]c thu[aậ]t/.test(txt)) cols.academic.push(r);
    else if (/trend|framework|tool|ai_research|công ngh[eệ]|dev/.test(txt)) cols.tech.push(r);
    else cols.market.push(r);
  }

  const urgentCount = metrics.keep_urgent;

  return (
    <div className="flex flex-col min-h-full gap-8 pb-10 animate-in fade-in duration-500">

      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-2xl font-black tracking-tight text-foreground flex items-center gap-3">
            <div className="p-2 rounded-xl bg-primary/10 border border-primary/20">
              <BarChart3 className="w-5 h-5 text-primary" />
            </div>
            Tổng quan thị trường
          </h1>
          <p className="text-[13px] text-muted-foreground mt-1">
            Bảng điều khiển thông tin thị trường cá nhân — Cập nhật realtime bởi AI Agent
          </p>
        </div>
        <div className="flex items-center gap-2 flex-wrap">
          <span className="flex items-center gap-1.5 text-[11px] border border-border/50 rounded-full px-3 py-1.5 text-muted-foreground bg-secondary/20">
            <span className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse" />
            Luồng tự động đang hoạt động
          </span>
          {metrics.last_run_at && (
            <span className="flex items-center gap-1.5 text-[11px] border border-border/50 rounded-full px-3 py-1.5 text-muted-foreground bg-secondary/20">
              <Clock className="w-3 h-3" />
              {relativeTime(metrics.last_run_at)}
            </span>
          )}
          <button
            onClick={handleTrigger}
            disabled={isTriggering}
            className="flex items-center gap-1.5 text-[12px] font-medium border border-border/60 rounded-full px-3 py-1.5 text-foreground bg-background hover:bg-secondary/60 disabled:opacity-50 transition-all cursor-pointer shadow-sm"
          >
            <RefreshCcw className={`w-3.5 h-3.5 ${isTriggering ? "animate-spin" : ""}`} />
            {isTriggering ? "Đang quét..." : "Lấy tin ngay"}
          </button>
        </div>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        {[
          { label: "Tin thu thập", value: metrics.total_today, cls: "text-foreground", sub: "bài hôm nay" },
          { label: "🔥 Tín hiệu nóng", value: metrics.keep_urgent, cls: "text-destructive font-black", sub: "cần đọc ngay" },
          { label: "📰 Đã lọc", value: metrics.keep, cls: "text-green-600 dark:text-green-400 font-black", sub: "tin chất lượng" },
          { label: "👀 Theo dõi", value: metrics.watch, cls: "text-amber-500 font-black", sub: "đang watch" },
          { label: "✅ Đã xử lý", value: metrics.processed, cls: "text-blue-600 dark:text-blue-400 font-black", sub: "báo cáo AI" },
          { label: "🗑️ Đã lọc bỏ", value: metrics.trash, cls: "text-muted-foreground", sub: "tin rác" },
        ].map(({ label, value, cls, sub }) => (
          <div key={label} className="bg-background border border-border/50 rounded-xl px-4 py-3.5 flex flex-col gap-1 hover:border-border transition-colors">
            <p className="text-[10px] font-medium text-muted-foreground/70 uppercase tracking-widest leading-none">{label}</p>
            <p className={`text-2xl tabular-nums leading-none mt-1 ${cls}`}>{value}</p>
            <p className="text-[11px] text-muted-foreground/50">{sub}</p>
          </div>
        ))}
      </div>

      {urgentCount > 0 && (
        <Link
          to="/feed?tab=KEEP_URGENT&page=1"
          className="flex items-center gap-4 p-4 bg-destructive/5 border border-destructive/30 rounded-xl hover:bg-destructive/10 transition-colors group"
        >
          <div className="p-2.5 bg-destructive/15 rounded-lg">
            <AlertTriangle className="w-5 h-5 text-destructive animate-pulse" />
          </div>
          <div className="flex-1">
            <p className="text-sm font-bold text-destructive">
              {urgentCount} tín hiệu thị trường quan trọng cần đọc ngay!
            </p>
            <p className="text-xs text-muted-foreground mt-0.5">
              AI đã phân tích và đánh dấu đây là những tin tức ưu tiên cao nhất cho bạn.
            </p>
          </div>
          <ExternalLink className="w-4 h-4 text-destructive/60 group-hover:text-destructive transition-colors" />
        </Link>
      )}

      <div>
        <div className="flex items-center gap-2 mb-4">
          <Zap className="w-4 h-4 text-primary" />
          <h2 className="text-sm font-bold text-foreground">Luồng Báo Cáo Chiến Lược</h2>
          <Badge variant="outline" className="text-[10px] font-mono ml-auto">{reports.length} báo cáo (có dẫn chứng)</Badge>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
          <ReportColumn title="Market Pulse" icon={<Activity className="w-3.5 h-3.5 text-blue-500" />} color="blue" items={cols.market} />
          <ReportColumn title="Việc làm & Nhân sự" icon={<Briefcase className="w-3.5 h-3.5 text-emerald-500" />} color="emerald" items={cols.jobs} />
          <ReportColumn title="Nghiên cứu Học thuật" icon={<Microscope className="w-3.5 h-3.5 text-orange-500" />} color="orange" items={cols.academic} />
          <ReportColumn title="Xu hướng Công nghệ" icon={<Cpu className="w-3.5 h-3.5 text-indigo-500" />} color="indigo" items={cols.tech} />
        </div>
      </div>

      {/* ── Job Watch Section ── */}
      <div className="bg-card border border-border/50 rounded-xl p-5">
        <JobWatchWidget />
      </div>

      <div className="fixed bottom-6 right-6 z-50">
        {isAssistantOpen ? (
          <div className="w-[360px] h-[500px] shadow-2xl flex flex-col rounded-2xl overflow-hidden border border-border bg-background animate-in slide-in-from-bottom-5 duration-300">
            <header className="p-4 border-b bg-primary text-primary-foreground flex items-center justify-between shrink-0">
              <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wide">
                <MessageSquare className="w-4 h-4" />
                Maestro AI Analyst
              </div>
              <Button variant="ghost" size="icon" className="h-7 w-7 hover:bg-white/20 text-primary-foreground"
                onClick={() => setIsAssistantOpen(false)}>
                <X className="w-4 h-4" />
              </Button>
            </header>
            <ScrollArea className="flex-1 p-4">
              <div className="space-y-3">
                {messages.map((m, i) => (
                  <div key={i} className={`text-[12px] leading-relaxed px-3 py-2.5 rounded-xl max-w-[90%] ${
                    m.role === "ai"
                      ? "bg-muted/60 text-foreground border border-border/50"
                      : "bg-primary/10 text-foreground border border-primary/20 ml-auto"
                  }`}>
                    {m.text}
                  </div>
                ))}
                {chatFetcher.state !== "idle" && (
                  <div className="text-[12px] px-3 py-2.5 rounded-xl bg-muted/60 border border-border/50 text-muted-foreground animate-pulse">
                    Đang phân tích...
                  </div>
                )}
              </div>
            </ScrollArea>
            <form onSubmit={handleChat} className="p-3 border-t bg-muted/20 shrink-0 flex gap-2">
              <Input name="prompt" placeholder="Hỏi về thị trường..." className="text-xs h-9 bg-background" autoComplete="off" />
              <Button size="icon" type="submit" className="h-9 w-9 shrink-0">
                <Send className="w-4 h-4" />
              </Button>
            </form>
          </div>
        ) : (
          <Button
            onClick={() => setIsAssistantOpen(true)}
            className="h-14 w-14 rounded-full shadow-2xl bg-primary text-primary-foreground hover:scale-110 transition-transform"
          >
            <MessageSquare className="w-6 h-6" />
          </Button>
        )}
      </div>
    </div>
  );
}

// ── Report Column Component ──
interface ReportColumnProps {
  title: string;
  icon: React.ReactNode;
  color: string;
  items: ResearchReport[];
}

function ReportColumn({ title, icon, color, items }: ReportColumnProps) {
  const colorBorder: Record<string, string> = {
    blue: "border-blue-200 dark:border-blue-800/30",
    emerald: "border-emerald-200 dark:border-emerald-800/30",
    orange: "border-orange-200 dark:border-orange-800/30",
    indigo: "border-indigo-200 dark:border-indigo-800/30",
  };

  return (
    <div className={`flex flex-col border border-border/50 rounded-xl overflow-hidden bg-card/30`}>
      <div className={`flex items-center gap-2 px-4 py-3 border-b ${colorBorder[color] || "border-border/50"} bg-muted/20 shrink-0`}>
        {icon}
        <h3 className="text-[11px] font-bold uppercase tracking-widest text-muted-foreground">{title}</h3>
        <Badge variant="outline" className="ml-auto text-[9px] font-mono">{items.length}</Badge>
      </div>
      <div className="flex flex-col divide-y divide-border/40 overflow-y-auto max-h-[480px]">
        {items.length === 0 && (
          <div className="py-12 text-center text-xs text-muted-foreground/40 italic">
            Chưa có báo cáo
          </div>
        )}
        {items.map(item => {
          const sent = getSentimentConfig(item.sentiment as string);
          const sourceUrl = item.original_source
            || item.source_citations?.[0]
            || item.sources?.[0];

          return (
            <div key={item.id} className="p-4 hover:bg-muted/20 transition-colors flex flex-col gap-2.5">
              <div className="flex items-center gap-2 flex-wrap">
                <span className={`inline-flex items-center gap-1 text-[10px] font-medium px-1.5 py-0.5 rounded-full border ${sent.cls}`}>
                  {sent.icon}{sent.label}
                </span>
                <span className="text-[10px] text-muted-foreground/50 tabular-nums ml-auto">
                  {relativeTime(item.created_at)}
                </span>
              </div>

              {/* Title — MUST link to source */}
              {sourceUrl ? (
                <a
                  href={sourceUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-[13px] font-bold text-foreground leading-snug hover:text-primary transition-colors line-clamp-2 flex items-start gap-1 group"
                >
                  <span>{item.title}</span>
                  <Globe className="w-3 h-3 text-muted-foreground/40 group-hover:text-primary shrink-0 mt-0.5 transition-colors" />
                </a>
              ) : (
                <p className="text-[13px] font-bold text-foreground/50 line-clamp-2 italic">
                  {item.title}
                  <span className="text-[10px] text-destructive/60 ml-1 font-normal">(thiếu nguồn)</span>
                </p>
              )}

              {/* Summary */}
              {(item.executive_summary || item.summary) && (
                <p className="text-[11px] text-muted-foreground leading-relaxed line-clamp-3 border-l-2 border-border/50 pl-2">
                  {item.executive_summary || item.summary}
                </p>
              )}

              {/* Footer: citation count + detail link */}
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
                  className="text-[10px] font-bold text-primary hover:underline flex items-center gap-0.5 uppercase tracking-wide"
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