import {
  Activity, ArrowRight, BookOpen, CheckCircle2,
  Clock, Info, Loader2, Microscope, Terminal, Zap, AlertCircle
} from "lucide-react";
import { Button } from "~/components/ui/button";
import { Link, useFetcher } from "react-router";
import { startResearch } from "~/lib/api";
import { Badge } from "~/components/ui/badge";
import type { Route } from "./+types/research";

type ActionData =
  | { success: true; report: { status: string; topic: string } }
  | { success: false; error: string };

export const meta: Route.MetaFunction = () => [
  { title: "Nghiên cứu chuyên sâu - TechScout Intelligence" },
  { name: "description", content: "Kích hoạt AI Agent nghiên cứu chuyên sâu về bất kỳ chủ đề công nghệ nào." }
];

export async function action({ request }: Route.ActionArgs) {
  const formData = await request.formData();
  const topic = formData.get("topic") as string;

  if (!topic?.trim()) {
    return { success: false, error: "Vui lòng nhập chủ đề nghiên cứu." };
  }

  try {
    const result = await startResearch(topic, true);
    return { success: true, report: result };
  } catch {
    return { success: false, error: "Agent protocol failure: Không thể truy cập luồng dữ liệu." };
  }
}

const EXAMPLE_TOPICS = [
  "Phân tích tác động của GPT-5 đến ngành lập trình Việt Nam 2025",
  "Xu hướng tuyển dụng AI Engineer tại Đông Nam Á Q2 2025",
  "So sánh các framework AI Agent: LangGraph vs CrewAI vs AutoGen",
  "Tác động của làn sóng layoff Big Tech đến thị trường IT Việt Nam",
];

export default function ResearchCenter() {
  const fetcher = useFetcher<ActionData>();
  const isRunning = fetcher.state !== "idle";
  const result = fetcher.data;

  return (
    <div className="max-w-4xl mx-auto flex flex-col gap-10 pb-16 motion-safe:animate-in motion-safe:fade-in motion-safe:duration-500">

      {/* ── HEADER ── */}
      <div className="flex flex-col gap-3 pt-4">
        <div className="flex items-center gap-2">
          <Microscope className="w-4 h-4 text-muted-foreground" />
          <h1 className="text-lg font-medium text-foreground tracking-tight">Nghiên cứu chuyên sâu</h1>
        </div>
        <p className="text-[12px] text-muted-foreground">AI Agent sẽ quét, tổng hợp và phân tích đa nguồn theo yêu cầu của bạn</p>

        {/* How it works */}
        <div className="flex items-start gap-3 p-4 bg-secondary/30 rounded-xl border border-border/50 mt-2">
          <Info className="w-4 h-4 text-muted-foreground shrink-0 mt-0.5" />
          <div className="space-y-1">
            <p className="text-[12px] font-medium text-foreground">Cách hoạt động</p>
            <p className="text-[12px] text-muted-foreground leading-relaxed">
              Nhập chủ đề bất kỳ → AI Agent thu thập nội dung từ nhiều nguồn báo uy tín (TechCrunch, The Verge, CNBC...) → Phân tích chuyên sâu bằng ReAct Loop → Sinh báo cáo có dẫn chứng link gốc cụ thể → Lưu vào thư viện báo cáo.
            </p>
          </div>
        </div>
      </div>

      {/* ── MAIN FORM ── */}
      <div className="bg-background border border-border/50 rounded-xl overflow-hidden">
        <div className="px-5 py-3 border-b border-border/50 flex items-center gap-2">
          <Zap className="w-4 h-4 text-muted-foreground" />
          <h2 className="text-[13px] font-medium text-foreground tracking-tight">Chủ đề nghiên cứu</h2>
          <Badge variant="outline" className="text-[9px] font-mono ml-auto">ReAct Engine v1.5</Badge>
        </div>

        <fetcher.Form method="post" className="p-6 flex flex-col gap-6">
          <div className="flex flex-col gap-2">
            <label htmlFor="research-topic" className="sr-only">Chủ đề nghiên cứu</label>
            <textarea
              id="research-topic"
              name="topic"
              required
              disabled={isRunning}
              rows={4}
              className="w-full bg-muted/30 border border-border/60 rounded-xl px-4 py-3.5 text-sm text-foreground focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 outline-none motion-safe:transition-colors placeholder:text-muted-foreground/40 font-medium disabled:opacity-60 resize-none"
              placeholder="Ví dụ: Phân tích sự dịch chuyển từ Microservices sang Monolith của các tập đoàn Tech năm 2025..."
            />
            <p className="text-[11px] text-muted-foreground/60">
              Mô tả chi tiết chủ đề để AI phân tích chính xác hơn. Kết quả sẽ bao gồm link dẫn chứng từ nguồn gốc.
            </p>
          </div>

          {/* Example topics */}
          <div className="flex flex-col gap-2">
            <p className="text-[10px] font-medium uppercase tracking-widest text-muted-foreground/60">Gợi ý chủ đề</p>
            <div className="flex flex-wrap gap-2">
              {EXAMPLE_TOPICS.map(t => (
                <button
                  key={t}
                  type="button"
                  disabled={isRunning}
                  onClick={(e) => {
                    const form = e.currentTarget.closest("form");
                    const textarea = form?.querySelector("textarea[name='topic']") as HTMLTextAreaElement;
                    if (textarea) textarea.value = t;
                  }}
                  aria-label={`Chọn chủ đề: ${t}`}
              className="text-[11px] px-3 py-1.5 rounded-full border border-border/60 bg-secondary/30 text-muted-foreground hover:bg-secondary hover:text-foreground motion-safe:transition-colors text-left disabled:opacity-50 cursor-pointer"
                >
                  {t}
                </button>
              ))}
            </div>
          </div>

          <Button
            type="submit"
            disabled={isRunning}
            className="h-12 gap-3 font-medium text-sm tracking-wide"
            size="lg"
          >
            {isRunning ? (
              <><Loader2 className="animate-spin w-5 h-5" /> Đang kích hoạt AI Agent...</>
            ) : (
              <><Zap className="w-5 h-5" /> Kích hoạt Nghiên cứu Chuyên sâu</>
            )}
          </Button>
        </fetcher.Form>
      </div>

      {/* ── RESULT / LOG PANEL ── */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Trace Log */}
        <div className="bg-background border border-border/50 rounded-2xl overflow-hidden">
          <div className="px-4 py-3 border-b border-border/50 flex items-center justify-between">
            <div className="flex items-center gap-2 text-[11px] font-medium text-muted-foreground uppercase tracking-wide">
              <Terminal className="w-3.5 h-3.5" />
              System Trace Log
            </div>
            <div className={`w-2 h-2 rounded-full ${isRunning ? "bg-primary motion-safe:animate-pulse" : result ? "bg-muted-foreground/60" : "bg-muted-foreground/30"}`} />
          </div>
          <div className="p-4 font-mono text-[11px] leading-relaxed h-48 overflow-y-auto space-y-1.5">
            {isRunning ? (
              <p className="text-muted-foreground motion-safe:animate-pulse">Request sent — pipeline is running in background...</p>
            ) : result?.success ? (
              <>
                <p className="text-foreground font-medium">[{new Date().toLocaleTimeString()}] COMPLETED ✓</p>
                <p className="text-muted-foreground">Topic: "{result.report.topic}"</p>
                <p className="text-muted-foreground">Status: {result.report.status}</p>
                <p className="text-green-600 dark:text-green-400 mt-2">→ Báo cáo đang được lưu vào thư viện...</p>
              </>
            ) : result?.success === false ? (
              <p className="text-destructive font-medium">[ERROR] {result.error}</p>
            ) : (
              <p className="text-muted-foreground/30 italic">Awaiting research command...</p>
            )}
          </div>
        </div>

        {/* Status Card */}
        <div className="bg-background border border-border/50 rounded-2xl flex flex-col items-center justify-center p-8 text-center gap-4">
          {result?.success ? (
            <div className="space-y-4 motion-safe:animate-in motion-safe:zoom-in-95 motion-safe:duration-500">
              <div className="mx-auto w-16 h-16 rounded-full bg-green-50 dark:bg-green-950/40 border border-green-200 dark:border-green-800/40 flex items-center justify-center">
                <CheckCircle2 className="w-8 h-8 text-green-600 dark:text-green-400" />
              </div>
              <div>
                <h3 className="font-medium text-sm text-foreground">Đang xử lý!</h3>
                <p className="text-[12px] text-muted-foreground mt-1 max-w-48 mx-auto">
                  AI Agent đang phân tích ngầm. Kết quả sẽ xuất hiện trong thư viện báo cáo.
                </p>
              </div>
              <Button asChild variant="outline" size="sm" className="gap-2 font-medium">
                <Link to="/reports">
                  <BookOpen className="w-4 h-4" />
                  Xem thư viện báo cáo
                  <ArrowRight className="w-3 h-3" />
                </Link>
              </Button>
            </div>
          ) : result?.success === false ? (
            <div className="opacity-80 flex flex-col items-center gap-3">
              <AlertCircle className="w-10 h-10 text-destructive/60" />
              <p className="text-sm font-medium text-destructive">Lỗi kết nối Agent</p>
              <p className="text-[11px] text-muted-foreground">{result.error}</p>
            </div>
          ) : isRunning ? (
            <div className="flex flex-col items-center gap-3">
              <div className="relative w-16 h-16">
                <div className="absolute inset-0 rounded-full border-4 border-primary/20" />
                <div className="absolute inset-0 rounded-full border-4 border-primary border-t-transparent motion-safe:animate-spin" />
              </div>
              <p className="text-[12px] font-medium text-muted-foreground uppercase tracking-wide motion-safe:animate-pulse">
                AI đang phân tích...
              </p>
              <p className="text-[11px] text-muted-foreground/60">Quá trình này có thể mất 1-3 phút</p>
            </div>
          ) : (
            <div className="flex flex-col items-center gap-3 opacity-30">
              <Clock className="w-10 h-10 text-muted-foreground" />
              <p className="text-[11px] font-medium uppercase tracking-widest text-muted-foreground">STANDBY</p>
              <p className="text-[11px] text-muted-foreground">Chờ lệnh nghiên cứu...</p>
            </div>
          )}
        </div>
      </div>

      {/* ── PIPELINE INFO ── */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {[
          {
            step: "01",
            title: "Scout & Thu thập",
            desc: "AI quét 25+ nguồn RSS, xác minh link sống, loại bỏ duplicate và link chết.",
            icon: <Activity className="w-4 h-4 text-blue-500" />,
          },
          {
            step: "02",
            title: "Gatekeeper Filter",
            desc: "Mô hình AI đọc tiêu đề & nội dung, chấm điểm tác động (0-10), phân loại theo whitelist topic.",
            icon: <Zap className="w-4 h-4 text-amber-500" />,
          },
          {
            step: "03",
            title: "Deep Analysis + Dẫn chứng",
            desc: "Jina Reader đọc toàn bộ bài gốc, ReAct Loop phân tích nhiều chiều, lưu kèm link nguồn xác minh.",
            icon: <Microscope className="w-4 h-4 text-muted-foreground" />,
          },
        ].map(({ title, desc, icon }) => (
          <div key={title} className="flex gap-4 p-4 bg-background border border-border/50 rounded-xl">
            <div className="flex flex-col items-center gap-2 shrink-0">
              <div className="p-2 bg-muted rounded-lg">{icon}</div>
            </div>
            <div>
              <p className="text-[13px] font-medium text-foreground">{title}</p>
              <p className="text-[12px] text-muted-foreground mt-1 leading-relaxed">{desc}</p>
            </div>
          </div>
        ))}
      </div>

    </div>
  );
}