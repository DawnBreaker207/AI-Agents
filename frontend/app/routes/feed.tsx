import type { Route } from "./+types/feed";
import { Link, useRevalidator } from "react-router";
import { useState, useEffect } from "react";
import { getNewsByStatus, getFeedMetrics, triggerPipeline } from "~/lib/api";
import { NewsCard } from "~/components/news-card";
import { cn, relativeTime } from "~/lib/utils";
import { Rss as RssIcon, Clock as ClockIcon, LayoutGrid, RefreshCcw } from "lucide-react";

export const meta: Route.MetaFunction = () => {
  return [
    { title: "Live News Feed - TechScout Control Center" },
    { name: "description", content: "Live News Feed monitored, analyzed, and filtered by TechScout AI Gatekeeper." }
  ];
};

export async function loader({ request }: Route.LoaderArgs) {
  const url = new URL(request.url);
  const tab = url.searchParams.get("tab") ?? "KEEP_URGENT";
  const page = Number(url.searchParams.get("page") ?? 1);

  try {
    const rawNews = await getNewsByStatus(tab, page);
    // CHUẨN HOÁ: Bất kể phần nào không có link gốc thì không được hiện lên trang feed
    const news = rawNews.filter(n => n.url && n.url.trim() !== "");
    return { tab, page, news };
  } catch (err) {
    console.error("Feed loader failed, returning empty state:", err);
    return { tab, page, news: [] };
  }
}

import { useOutletContext } from "react-router";
import type { FeedMetrics } from "~/types";

export default function Feed({ loaderData }: Route.ComponentProps) {
  const { tab, page, news } = loaderData;
  const { metrics } = useOutletContext<{ metrics: FeedMetrics }>();
  const [isTriggering, setIsTriggering] = useState(false);
  const { revalidate, state } = useRevalidator();

  // 1. SSE Realtime Connection with robust reconnect
  useEffect(() => {
    let sse: EventSource | null = null;
    let retryCount = 0;
    let timeoutId: NodeJS.Timeout;

    const connect = () => {
      sse = new EventSource("http://localhost:8888/api/news/stream");
      
      sse.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === "new_news" && state === "idle") {
            revalidate(); // Tự động cập nhật data khi có tin mới
          }
        } catch (e) {}
      };

      sse.onerror = () => {
        sse?.close();
        const delay = Math.min(10000, 1000 * Math.pow(2, retryCount));
        retryCount++;
        timeoutId = setTimeout(connect, delay);
      };

      sse.onopen = () => {
        retryCount = 0;
      };
    };

    connect();

    return () => {
      sse?.close();
      clearTimeout(timeoutId);
    };
  }, [state, revalidate]);

  const handleTrigger = async () => {
    setIsTriggering(true);
    try {
      await triggerPipeline();
      alert("Đã kích hoạt quét tin tức thủ công. Hệ thống đang thu thập và phân tích nền!");
      revalidate();
    } catch (e) {
      alert("Lỗi kích hoạt pipeline.");
    } finally {
      setIsTriggering(false);
    }
  };

  const TABS_MAP = [
    { id: "KEEP_URGENT", label: "🔥 Tin Nóng Đầu Tư / Quan Trọng", count: metrics.keep_urgent },
    { id: "KEEP",        label: "📰 Tin Tức Đã Lọc", count: metrics.keep },
    { id: "WATCH",       label: "👀 Đang Theo Dõi (Watch)", count: metrics.watch },
    { id: "PENDING",     label: "⏳ Chờ AI Phân Tích", count: metrics.total_today - metrics.processed },
  ] as const;

  return (
    <div className="flex flex-col gap-8 animate-in fade-in duration-500 max-w-7xl mx-auto pb-16">
      
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-3">
        <div className="space-y-0.5">
          <h1 id="page-title" className="text-lg font-medium text-foreground tracking-tight flex items-center gap-2">
            <RssIcon className="w-4 h-4 text-muted-foreground" />
            Live Feed
          </h1>
          <p className="text-[12px] text-muted-foreground leading-relaxed">
            Luồng tin tức công nghệ thời gian thực được rà quét và phân loại tự động.
          </p>
        </div>

        <div className="flex items-center gap-2 flex-wrap">
          <span className="flex items-center gap-1.5 text-[11px] border border-border/50 rounded-full px-2.5 py-1 text-muted-foreground bg-secondary/20">
            <span className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse" />
            Pipeline đang hoạt động
          </span>

          <span className="flex items-center gap-1 text-[11px] border border-border/50 rounded-full px-2.5 py-1 text-muted-foreground bg-secondary/20">
            <ClockIcon className="w-3 h-3" />
            Cập nhật {relativeTime(metrics.last_run_at ?? new Date().toISOString())}
          </span>
          
          <button 
            onClick={handleTrigger}
            disabled={isTriggering}
            className="flex items-center gap-1.5 text-[11px] border border-border/50 rounded-full px-2.5 py-1 text-foreground bg-background hover:bg-secondary/60 disabled:opacity-50 transition-colors cursor-pointer"
          >
            <RefreshCcw className={cn("w-3 h-3", isTriggering && "animate-spin")} />
            {isTriggering ? "Đang quét..." : "Lấy tin ngay"}
          </button>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-2.5">
        <div className="bg-background border border-border/50 rounded-lg px-3.5 py-3 flex flex-col justify-between">
          <div>
            <p className="text-[10px] font-medium text-muted-foreground/60 uppercase tracking-widest mb-1">Tin thu thập hôm nay</p>
            <p className="text-3xl font-black text-foreground leading-none tabular-nums">
              {metrics.total_today}
            </p>
          </div>
          <p className="text-[11px] text-muted-foreground/60 mt-1.5">bài đã xử lý</p>
        </div>

        <div className="bg-background border border-border/50 rounded-lg px-3.5 py-3 flex flex-col justify-between">
          <div>
            <p className="text-[10px] font-medium text-muted-foreground/60 uppercase tracking-widest mb-1 text-destructive">Tín hiệu Quan trọng</p>
            <p className="text-3xl font-black text-destructive leading-none tabular-nums">
              {metrics.keep_urgent}
            </p>
          </div>
          <p className="text-[11px] text-muted-foreground/60 mt-1.5">cần đọc ngay</p>
        </div>

        <div className="bg-background border border-border/50 rounded-lg px-3.5 py-3 flex flex-col justify-between">
          <div>
            <p className="text-[10px] font-medium text-muted-foreground/60 uppercase tracking-widest mb-1 text-green-600 dark:text-green-400">Tin tức Chất lượng</p>
            <p className="text-3xl font-black text-green-600 dark:text-green-400 leading-none tabular-nums">
              {metrics.keep}
            </p>
          </div>
          <p className="text-[11px] text-muted-foreground/60 mt-1.5">trong hàng đợi</p>
        </div>

        <div className="bg-background border border-border/50 rounded-lg px-3.5 py-3 flex flex-col justify-between">
          <div>
            <p className="text-[10px] font-medium text-muted-foreground/60 uppercase tracking-widest mb-1 text-amber-600 dark:text-amber-400">Tin Bình Thường (Watch)</p>
            <p className="text-3xl font-black text-amber-600 dark:text-amber-400 leading-none tabular-nums">
              {metrics.watch}
            </p>
          </div>
          <p className="text-[11px] text-muted-foreground/60 mt-1.5">đang theo dõi</p>
        </div>
      </div>

      <div className="flex items-center gap-1.5 border-b border-border/50 mt-1 overflow-x-auto pb-px">
        {TABS_MAP.map((t) => (
          <Link
            key={t.id}
            to={`?tab=${t.id}&page=1`}
            className={cn(
              "flex items-center gap-2 px-4 py-2.5 text-[13px] border-b-2 -mb-[2px] transition-all whitespace-nowrap rounded-t-lg",
              tab === t.id
                ? "border-primary text-primary font-bold bg-primary/5"
                : "border-transparent text-muted-foreground hover:text-foreground hover:bg-secondary/40"
            )}
          >
            {t.label}
            <span className={cn(
              "text-[10px] px-2 py-0.5 rounded-full transition-colors font-mono",
              tab === t.id
                ? "bg-primary text-primary-foreground"
                : "bg-secondary text-muted-foreground"
            )}>
              {t.count}
            </span>
          </Link>
        ))}
      </div>

      {/* ── NEWS LIST (GRID/MASONRY LAYOUT) ── */}
      <div className={cn(
        "grid gap-4",
        tab === "KEEP_URGENT" ? "grid-cols-1 md:grid-cols-2" : "grid-cols-1 md:grid-cols-2 lg:grid-cols-3"
      )}>
        {news.map((item, idx) => (
          <NewsCard 
            key={item.id} 
            news={item} 
            showPromote={false} 
            queuePos={(tab === "KEEP") ? (page - 1) * 20 + idx + 1 : undefined} 
          />
        ))}

        {news.length === 0 && (
          <div className="col-span-full py-24 text-center flex flex-col items-center gap-4 border border-dashed border-border/60 rounded-xl bg-card/20 backdrop-blur-sm">
            <div className="p-4 bg-secondary/30 rounded-full">
              <LayoutGrid className="w-8 h-8 text-muted-foreground/50 animate-pulse" />
            </div>
            <p className="text-sm font-bold text-muted-foreground uppercase tracking-widest">
              Không có tin tức thị trường nào ở danh mục này
            </p>
            <p className="text-[12px] text-muted-foreground/60 italic max-w-sm leading-relaxed">
              Các nguồn dữ liệu đang được AI Agent quét liên tục. Kết quả mới nhất sẽ tự động hiện lên đây (Real-time).
            </p>
          </div>
        )}
      </div>

      {/* ── PAGINATION (Antes / Next) ── */}
      {news.length > 0 && (
        <div className="flex items-center justify-between pt-4 border-t border-border/50">
          <Link
            to={`/feed?tab=${tab}&page=${page > 1 ? page - 1 : 1}`}
            className={cn(
              "px-3 py-1.5 rounded text-[13px] font-medium transition-colors border border-border/50 bg-background text-foreground hover:bg-secondary/60",
              page <= 1 && "pointer-events-none opacity-40 bg-muted"
            )}
          >
            Trước
          </Link>
          <span className="text-[11px] font-mono text-muted-foreground font-medium">
            Trang {page}
          </span>
          <Link
            to={`/feed?tab=${tab}&page=${page + 1}`}
            className={cn(
              "px-3 py-1.5 rounded text-[13px] font-medium transition-colors border border-border/50 bg-background text-foreground hover:bg-secondary/60",
              news.length < 20 && "pointer-events-none opacity-40 bg-muted"
            )}
          >
            Tiếp
          </Link>
        </div>
      )}

    </div>
  );
}

import { isRouteErrorResponse } from "react-router";

export function ErrorBoundary({ error }: Route.ErrorBoundaryProps) {
  if (isRouteErrorResponse(error)) {
    return (
      <div className="flex flex-col items-center justify-center py-24 text-center max-w-lg mx-auto">
        <div className="bg-destructive/10 p-4 rounded-full mb-4">
          <RefreshCcw className="w-8 h-8 text-destructive animate-pulse" />
        </div>
        <h1 className="text-xl font-bold mb-2">Lỗi tải dữ liệu</h1>
        <p className="text-muted-foreground mb-6">
          {error.status} {error.statusText}
        </p>
        <Link to="/feed" className="bg-primary text-primary-foreground px-6 py-2 rounded-full text-sm font-medium hover:bg-primary/90 transition-colors">
          Thử lại
        </Link>
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center justify-center py-24 text-center max-w-lg mx-auto">
      <div className="bg-destructive/10 p-4 rounded-full mb-4">
        <RefreshCcw className="w-8 h-8 text-destructive" />
      </div>
      <h1 className="text-xl font-bold mb-2">Có lỗi xảy ra</h1>
      <p className="text-muted-foreground mb-6">
        Hệ thống không thể tải luồng tin tức lúc này. Vui lòng kiểm tra kết nối mạng hoặc thử lại sau.
      </p>
      <button 
        onClick={() => window.location.reload()} 
        className="bg-primary text-primary-foreground px-6 py-2 rounded-full text-sm font-medium hover:bg-primary/90 transition-colors"
      >
        Tải lại trang
      </button>
    </div>
  );
}