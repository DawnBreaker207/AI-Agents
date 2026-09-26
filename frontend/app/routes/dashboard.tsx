import { Link, useRevalidator } from "react-router";
import {
  Activity,
  ExternalLink, RefreshCcw, AlertTriangle,
  BarChart3, Zap, Clock
} from "lucide-react";
import { getStrategicReports, getFeedMetrics, triggerPipeline, getJobWatches, addJobWatch, deleteJobWatch, API_BASE_URL } from "~/lib/api";
import { useState, useEffect, useRef } from "react";
import type { Route } from "./+types/dashboard";
import type { FeedMetrics } from "~/types";
import { relativeTime } from "~/lib/utils";
import { getSentimentConfig, SENTIMENT_BORDER } from "~/lib/constants";
import { toast } from "sonner";
import JobWatchWidget from "~/components/job/job-watch-widget";

export const meta: Route.MetaFunction = () => [
  { title: "Tổng quan thị trường - TechScout Intelligence" },
  { name: "description", content: "Bảng điều khiển thông tin thị trường công nghệ cá nhân được phân tích bởi AI." }
];

export async function loader({ request }: Route.LoaderArgs) {
  try {
    const [strategic, metrics, watches] = await Promise.all([
      getStrategicReports("all"),
      getFeedMetrics(),
      getJobWatches(),
    ]);

    // Preview ngắn: 5 report mới nhất có nguồn — chi tiết đầy đủ ở /reports
    const reports = strategic.filter(r => {
      const hasSource = (r.original_source && r.original_source.trim() !== "")
        || (r.source_citations && r.source_citations.length > 0);
      return hasSource;
    }).slice(0, 5);

    return { reports, metrics, watches };
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
  const [isTriggering, setIsTriggering] = useState(false);

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

  // Preview ngắn — phân loại chi tiết ở /reports, dashboard không tự vẽ lại
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
          <h2 className="text-[13px] font-medium text-foreground">Báo cáo mới nhất</h2>
          <Link to="/reports" className="text-[12px] text-muted-foreground hover:text-foreground ml-auto">
            Xem tất cả →
          </Link>
        </div>
        <div className="flex flex-col gap-2">
          {reports.map(r => (
            <Link key={r.id} to={`/reports/${r.id}`}
              className="bg-background border border-border/50 rounded-lg px-4 py-3 hover:border-border transition-colors">
              <p className="text-[13px] font-medium text-foreground leading-snug line-clamp-1">{r.title}</p>
              {r.executive_summary && (
                <p className="text-[12px] text-muted-foreground leading-relaxed line-clamp-1 mt-1">
                  {r.executive_summary.slice(0, 160)}
                </p>
              )}
            </Link>
          ))}
          {reports.length === 0 && (
            <p className="text-[12px] text-muted-foreground">Chưa có báo cáo nào.</p>
          )}
        </div>
      </div>

      {/* ── Job Watch Section ── */}
      <div className="bg-card border border-border/50 rounded-xl p-5">
        <JobWatchWidget watches={watches ?? []} />
      </div>

    </div>
  );
}

