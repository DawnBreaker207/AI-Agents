import type { Route } from "./+types/reports";
import { getStrategicReports, getReportHistory } from "~/lib/api";
import { FileText, Search, Filter } from "lucide-react";
import { Button } from "~/components/ui/button";
import { Input } from "~/components/ui/input";
import { Form, useSubmit, useNavigation } from "react-router";
import { ReportCard } from "~/components/ReportCard";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "~/components/ui/select";

export async function loader({ request }: Route.LoaderArgs) {
  const url = new URL(request.url);
  const search = url.searchParams.get("search")?.toLowerCase() || "";
  const category = url.searchParams.get("category") || "all";

  try {
    const [strategic, history] = await Promise.all([
      getStrategicReports(),
      getReportHistory()
    ]);

    // Combine and deduplicate reports
    const allReports = [...strategic, ...history];
    const seen = new Set<number>();
    let reports = allReports.filter(r => {
      // Bắt buộc phải có nguồn (link)
      const hasSource = (r.original_source && r.original_source.trim() !== "") || (r.source_citations && r.source_citations.length > 0);
      if (!hasSource) return false;
      
      if (seen.has(r.id)) return false;
      seen.add(r.id);
      return true;
    });

    // Apply filters
    if (search) {
      reports = reports.filter(r => 
        r.title.toLowerCase().includes(search) || 
        (r.executive_summary || r.summary || "").toLowerCase().includes(search)
      );
    }

    if (category && category !== "all") {
      reports = reports.filter(r => {
        const rawCategory = r.categories?.[0] || r.tags?.[0] || "OTHER";
        return rawCategory === category;
      });
    }

    return { reports, search, category };
  } catch (err) {
    console.error("Reports loader failed, returning empty state:", err);
    return { reports: [], search, category };
  }
}

export default function ReportsPage({ loaderData }: Route.ComponentProps) {
  const { reports, search, category } = loaderData;
  const submit = useSubmit();
  const navigation = useNavigation();
  const isSearching = navigation.state === "loading";

  const handleSearchChange = (e: React.FormEvent<HTMLFormElement>) => {
    // Automatically submit form on changes for a dynamic real-time experience
    submit(e.currentTarget, { replace: true });
  };

  const categories = [
    { value: "all", label: "Tất cả danh mục" },
    { value: "AI_RESEARCH", label: "AI Research" },
    { value: "LAYOFF", label: "Layoff News" },
    { value: "VN_MARKET", label: "Vietnam Market" },
    { value: "DEV_TOOLS", label: "Developer Tools" },
    { value: "SECURITY", label: "Security & Security News" },
    { value: "BUSINESS", label: "Business Intel" },
    { value: "OTHER", label: "Khác" }
  ];

  return (
    <div className="space-y-8 animate-in fade-in duration-500 max-w-5xl mx-auto pb-16">
      
      {/* ── HEADER ── */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-6 border-b pb-8 border-border/50">
        <div className="space-y-1">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-primary rounded-lg shadow-xl shadow-primary/20">
              <FileText className="text-primary-foreground" size={24} />
            </div>
            <h2 className="text-3xl font-black tracking-tighter italic text-foreground uppercase">
              Insight Reports
            </h2>
          </div>
          <p className="text-muted-foreground font-medium text-sm max-w-md italic">
            Thư viện bóc tách tri thức chiến lược từ Agentic AI - Cập nhật liên tục.
          </p>
        </div>
      </div>

      {/* ── FILTER & SEARCH PANEL ── */}
      <Form 
        method="get" 
        onChange={handleSearchChange} 
        className="flex flex-col md:flex-row gap-4 p-4 rounded-2xl border bg-card/40 backdrop-blur-sm shadow-sm"
      >
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground/60" />
          <Input 
            name="search" 
            defaultValue={search} 
            placeholder="Tìm kiếm theo tiêu đề hoặc nội dung..." 
            className="pl-9 h-10 text-xs bg-background"
          />
        </div>
        
        <div className="w-full md:w-56">
          <Select 
            name="category" 
            defaultValue={category} 
            onValueChange={(val) => {
              const form = document.querySelector("form[method='get']") as HTMLFormElement;
              if (form) submit(form, { replace: true });
            }}
          >
            <SelectTrigger className="h-10 text-xs bg-background">
              <SelectValue placeholder="Chọn danh mục" />
            </SelectTrigger>
            <SelectContent>
              {categories.map(cat => (
                <SelectItem key={cat.value} value={cat.value} className="text-xs">
                  {cat.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </Form>

      {/* ── REPORTS GRID ── */}
      {isSearching ? (
        <div className="grid gap-6 md:grid-cols-2 animate-pulse">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="h-64 bg-muted rounded-2xl" />
          ))}
        </div>
      ) : reports.length > 0 ? (
        <div className="grid gap-6 md:grid-cols-2">
          {reports.map((report) => (
            <ReportCard key={report.id} report={report} />
          ))}
        </div>
      ) : (
        <div className="py-32 text-center flex flex-col items-center gap-4 opacity-30">
          <Search size={48} className="animate-pulse text-muted-foreground" />
          <p className="font-black uppercase tracking-[0.3em] text-sm">Không tìm thấy báo cáo nào</p>
          <p className="text-xs text-muted-foreground italic">Hãy thử thay đổi từ khóa hoặc bộ lọc danh mục.</p>
        </div>
      )}
      
    </div>
  );
}