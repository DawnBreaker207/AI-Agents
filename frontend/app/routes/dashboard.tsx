import { Link, useFetcher, useRevalidator } from "react-router";
import { Input } from "~/components/ui/input";
import { Button } from "~/components/ui/button";
import { ScrollArea } from "~/components/ui/scroll-area";
import { Badge } from "~/components/ui/badge";
import {
  Activity, Briefcase, Cpu, MessageSquare, Microscope,
  Send, X,
  ExternalLink, RefreshCcw, AlertTriangle,
  BarChart3, Zap, Clock
} from "lucide-react";
import { getStrategicReports, getReportHistory, chatWithAgent, getFeedMetrics, triggerPipeline, getJobWatches, addJobWatch, deleteJobWatch, API_BASE_URL } from "~/lib/api";
import { useState, useEffect, useRef } from "react";
import type { Route } from "./+types/dashboard";
import type { ResearchReport, FeedMetrics } from "~/types";
import { relativeTime } from "~/lib/utils";
import { getSentimentConfig, SENTIMENT_BORDER } from "~/lib/constants";
import { toast } from "sonner";
import { ReportColumn } from "~/components/report/report-column";
import JobWatchWidget from "~/components/job/job-watch-widget";

export const meta: Route.MetaFunction = () => [
  { title: "Tổng quan thị trường - TechScout Intelligence" },
  { name: "description", content: "Bảng điều khiển thông tin thị trường công nghệ cá nhân được phân tích bởi AI." }
];

export async function loader({ request }: Route.LoaderArgs) {
  try {
    const [strategic, history, metrics, watches] = await Promise.all([
      getStrategicReports(),
      getReportHistory(),
      getFeedMetrics(),
      getJobWatches(),
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

    return { reports: allReports, metrics, watches };
  } catch (err) {
    console.error("Dashboard loader failed:", err);
    return {
      reports: [],
      watches: [],
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

  if (intent === "addWatch") {
    const position = formData.get("position") as string;
    const level = (formData.get("level") as string) ?? "Tất cả";
    const locationType = (formData.get("location_type") as string) ?? "domestic";
    const city = (formData.get("city") as string) ?? "Tất cả";
    try {
      await addJobWatch(position, level, locationType, city);
      return { ok: true };
    } catch {
      return { ok: false, error: "Không thể thêm vị trí." };
    }
  }

  if (intent === "deleteWatch") {
    const watchId = Number(formData.get("watchId"));
    try {
      await deleteJobWatch(watchId);
      return { ok: true };
    } catch {
      return { ok: false, error: "Không thể xóa vị trí." };
    }
  }

  return {};
}

export default function Dashboard({ loaderData }: Route.ComponentProps) {
  const { reports, metrics, watches } = loaderData;
  const { revalidate, state } = useRevalidator();
  const [isAssistantOpen, setIsAssistantOpen] = useState(false);
  const [isTriggering, setIsTriggering] = useState(false);
  const [messages, setMessages] = useState<{ role: "ai" | "user"; text: string }[]>([
    { role: "ai", text: "Chào! Tôi đang giám sát luồng báo cáo thị trường. Bạn muốn tôi phân tích điều gì?" }
  ]);
  const chatFetcher = useFetcher<{ answer: string }>();

  // SSE Realtime
  const revalidatorRef = useRef(revalidate);
  revalidatorRef.current = revalidate;
  useEffect(() => {
    const sse = new EventSource(`${API_BASE_URL}/api/news/stream`);
    sse.onmessage = () => {
      if (state === "idle") revalidatorRef.current();
    };
    return () => sse.close();
  }, []);

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
      toast.success("Pipeline đã kích hoạt", {
        description: "Hệ thống đang thu thập và phân tích tin tức nền.",
      });
      revalidate();
    } catch {
      toast.error("Lỗi kích hoạt pipeline", {
        description: "Không thể kết nối backend. Vui lòng thử lại sau.",
      });
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
    <div className="flex flex-col min-h-full gap-6 pb-10 motion-safe:animate-in motion-safe:fade-in motion-safe:duration-500">

      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-lg font-medium text-foreground tracking-tight flex items-center gap-2">
            <BarChart3 className="w-4 h-4 text-muted-foreground" />
            Tổng quan thị trường
          </h1>
          <p className="text-[12px] text-muted-foreground mt-0.5">
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
            type="button"
            onClick={handleTrigger}
            disabled={isTriggering}
            className="flex items-center gap-1.5 text-[12px] font-medium border border-border/60 rounded-full px-4 py-2 text-foreground bg-background hover:bg-secondary/60 disabled:opacity-50 transition-colors cursor-pointer min-h-11"
          >
            <RefreshCcw className={`w-3.5 h-3.5 ${isTriggering ? "animate-spin" : ""}`} />
            {isTriggering ? "Đang quét..." : "Lấy tin ngay"}
          </button>
        </div>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2.5">
        {[
          { label: "Tin thu thập", value: metrics.total_today, cls: "text-foreground", sub: "bài hôm nay", icon: Activity },
          { label: "Tín hiệu nóng", value: metrics.keep_urgent, cls: "text-destructive", sub: "cần đọc ngay", icon: AlertTriangle },
          { label: "Đã lọc", value: metrics.keep, cls: "text-green-600 dark:text-green-400", sub: "tin chất lượng", icon: Zap },
          { label: "Theo dõi", value: metrics.watch, cls: "text-amber-600 dark:text-amber-400", sub: "đang theo dõi", icon: BarChart3 },
          { label: "Đã xử lý", value: metrics.processed, cls: "text-blue-600 dark:text-blue-400", sub: "báo cáo AI", icon: Activity },
          { label: "Đã lọc bỏ", value: metrics.trash, cls: "text-muted-foreground/60", sub: "tin rác", icon: BarChart3 },
        ].map(({ label, value, cls, sub, icon: Icon }) => (
          <div key={label} className="group bg-background border border-border/50 rounded-lg px-3.5 py-3 flex flex-col gap-1 hover:border-border/80 hover:bg-muted/20 transition-colors cursor-default">
            <div className="flex items-center gap-1.5">
              <Icon className="w-3 h-3 text-muted-foreground/40 group-hover:text-muted-foreground/70 transition-colors" />
              <p className="text-[11px] text-muted-foreground tracking-wide leading-none">{label}</p>
            </div>
            <p className={`text-2xl font-medium leading-none mt-1 tabular-nums ${cls}`}>{value}</p>
            <p className="text-[11px] text-muted-foreground/60">{sub}</p>
          </div>
        ))}
      </div>

      {urgentCount > 0 && (
        <Link
          to="/feed?tab=KEEP_URGENT&page=1"
          className="flex items-center gap-4 p-4 bg-destructive/5 border border-destructive/30 rounded-xl hover:bg-destructive/10 transition-colors group"
        >
          <div className="p-2.5 bg-destructive/15 rounded-lg">
            <AlertTriangle className="w-5 h-5 text-destructive" />
          </div>
          <div className="flex-1">
            <p className="text-sm font-medium text-destructive">
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
          <Zap className="w-4 h-4 text-muted-foreground" />
          <h2 className="text-[13px] font-medium text-foreground">Luồng Báo Cáo Chiến Lược</h2>
          <Badge variant="outline" className="text-[10px] font-mono ml-auto">{reports.length} báo cáo (có dẫn chứng)</Badge>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
          <ReportColumn title="Market Pulse" icon={<Activity className="w-3.5 h-3.5 text-blue-500" />} color="blue" items={cols.market} />
          <ReportColumn title="Việc làm & Nhân sự" icon={<Briefcase className="w-3.5 h-3.5 text-muted-foreground" />} color="accent" items={cols.jobs} />
          <ReportColumn title="Nghiên cứu Học thuật" icon={<Microscope className="w-3.5 h-3.5 text-orange-500" />} color="orange" items={cols.academic} />
          <ReportColumn title="Xu hướng Công nghệ" icon={<Cpu className="w-3.5 h-3.5 text-muted-foreground" />} color="accent" items={cols.tech} />
        </div>
      </div>

      {/* ── Job Watch Section ── */}
      <div className="bg-card border border-border/50 rounded-xl p-5">
        <JobWatchWidget watches={watches ?? []} />
      </div>

      <div className="fixed bottom-6 right-6 z-50">
        {isAssistantOpen ? (
          <div className="w-[calc(100vw-2rem)] sm:w-[360px] max-w-[360px] h-[500px] flex flex-col rounded-xl overflow-hidden border border-border bg-background motion-safe:animate-in motion-safe:slide-in-from-bottom-5 motion-safe:duration-300">
            <header className="p-4 border-b bg-primary text-primary-foreground flex items-center justify-between shrink-0">
              <div className="flex items-center gap-2 text-xs font-medium uppercase tracking-wide">
                <MessageSquare className="w-4 h-4" />
                Maestro AI Analyst
              </div>
              <Button variant="ghost" size="icon" className="min-h-11 min-w-11 hover:bg-white/20 text-primary-foreground"
                onClick={() => setIsAssistantOpen(false)}
                aria-label="Đóng chat">
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
                  <div className="text-[12px] px-3 py-2.5 rounded-xl bg-muted/60 border border-border/50 text-muted-foreground motion-safe:animate-pulse">
                    Đang phân tích...
                  </div>
                )}
              </div>
            </ScrollArea>
            <form onSubmit={handleChat} className="p-3 border-t bg-muted/20 shrink-0 flex gap-2" aria-label="Chat với AI Analyst">
              <label htmlFor="chat-prompt" className="sr-only">Câu hỏi về thị trường</label>
              <Input id="chat-prompt" name="prompt" placeholder="Hỏi về thị trường..." className="text-xs min-h-11 bg-background" autoComplete="off" />
              <Button size="icon" type="submit" className="min-h-11 min-w-11 shrink-0" aria-label="Gửi câu hỏi">
                <Send className="w-4 h-4" />
              </Button>
            </form>
          </div>
        ) : (
          <Button
            onClick={() => setIsAssistantOpen(true)}
            className="h-14 w-14 rounded-full bg-primary text-primary-foreground hover:scale-110 motion-safe:transition-transform"
            aria-label="Mở chat AI Analyst"
          >
            <MessageSquare className="w-6 h-6" />
          </Button>
        )}
      </div>
    </div>
  );
}

