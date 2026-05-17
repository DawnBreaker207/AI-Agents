import { useState, useEffect } from "react";
import { useSearchParams } from "react-router";
import { Search, Briefcase, MapPin, Globe, Building2, ExternalLink } from "lucide-react";
import type { Route } from "./+types/jobs";

interface Job {
  id: string;
  title: string;
  company: string;
  location: string;
  location_type: string;
  work_model: string;
  url: string;
  source: string;
  description: string;
  posted_at: string | null;
}

const LEVELS = ["Tất cả", "Intern", "Junior", "Middle", "Senior", "Lead / Principal"];
const CITIES = ["Tất cả", "Hà Nội", "Hồ Chí Minh", "Đà Nẵng", "Khác"];

export default function JobsPage() {
  const [searchParams] = useSearchParams();

  const [keyword, setKeyword] = useState(() => searchParams.get("keyword") ?? "");
  const [level, setLevel] = useState(() => searchParams.get("level") ?? "Tất cả");
  const [city, setCity] = useState(() => searchParams.get("city") ?? "Tất cả");
  const [locationType, setLocationType] = useState<"domestic" | "overseas">(
    () => (searchParams.get("location_type") as "domestic" | "overseas") ?? "domestic"
  );
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Auto-run search if coming from a deep-link with params
  useEffect(() => {
    if (keyword || level !== "Tất cả") {
      runSearch(keyword, level, locationType, city);
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const runSearch = async (kw: string, lv: string, lt: string, ct: string) => {
    setLoading(true);
    setError("");
    try {
      const params = new URLSearchParams({ keyword: kw, location_type: lt, level: lv });
      if (lt === "domestic") params.set("city", ct);
      const res = await fetch(`http://localhost:8888/api/jobs/search?${params}`);
      if (!res.ok) throw new Error("Lỗi khi tải dữ liệu công việc.");
      const data = await res.json();
      setJobs(data.data || []);
    } catch (err: any) {
      setError(err.message || "Đã xảy ra lỗi.");
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!keyword.trim() && level === "Tất cả") return;
    runSearch(keyword, level, locationType, city);
  };

  return (
    <div className="flex flex-col gap-6 w-full h-full pb-10">
      <div className="flex flex-col gap-2">
        <h1 className="text-2xl font-bold tracking-tight">Tìm Kiếm Việc Làm</h1>
        <p className="text-sm text-muted-foreground">
          Khám phá cơ hội nghề nghiệp từ các nguồn uy tín. Hỗ trợ tìm việc trực tiếp trong nước và việc làm từ xa quốc tế.
        </p>
      </div>

      <div className="bg-card border border-border/50 rounded-xl p-5 shadow-sm">
        <form onSubmit={handleSearch} className="flex flex-col gap-4">
          <div className="flex flex-col xl:flex-row gap-4 items-end">
            
            <div className="flex-1 w-full space-y-1.5 min-w-[200px]">
              <label className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Vị trí tuyển dụng (VD: React, Python...)</label>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                <input
                  type="text"
                  value={keyword}
                  onChange={(e) => setKeyword(e.target.value)}
                  placeholder="VD: Frontend, React, Python, VNG..."
                  className="w-full pl-9 pr-4 py-2.5 bg-background border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary/20 transition-all"
                />
              </div>
            </div>

            <div className="w-full xl:w-48 space-y-1.5 shrink-0">
              <label className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Trình độ / Level</label>
              <select
                value={level}
                onChange={(e) => setLevel(e.target.value)}
                className="w-full px-3 py-2.5 bg-background border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary/20 transition-all appearance-none"
              >
                {LEVELS.map(l => (
                  <option key={l} value={l}>{l}</option>
                ))}
              </select>
            </div>

            <div className="w-full xl:w-64 space-y-1.5 shrink-0">
              <label className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Loại việc làm</label>
              <div className="flex bg-background border border-border rounded-lg overflow-hidden p-1">
                <button
                  type="button"
                  onClick={() => setLocationType("domestic")}
                  className={`flex-1 flex items-center justify-center gap-1.5 py-1.5 text-xs font-medium rounded-md transition-all ${
                    locationType === "domestic" ? "bg-primary text-primary-foreground shadow-sm" : "text-muted-foreground hover:bg-secondary/50"
                  }`}
                >
                  <MapPin className="w-3.5 h-3.5" />
                  Trong nước
                </button>
                <button
                  type="button"
                  onClick={() => setLocationType("overseas")}
                  className={`flex-1 flex items-center justify-center gap-1.5 py-1.5 text-xs font-medium rounded-md transition-all ${
                    locationType === "overseas" ? "bg-primary text-primary-foreground shadow-sm" : "text-muted-foreground hover:bg-secondary/50"
                  }`}
                >
                  <Globe className="w-3.5 h-3.5" />
                  Quốc tế
                </button>
              </div>
            </div>

            {locationType === "domestic" && (
              <div className="w-full xl:w-40 space-y-1.5 shrink-0">
                <label className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Thành phố</label>
                <select
                  value={city}
                  onChange={(e) => setCity(e.target.value)}
                  className="w-full px-3 py-2.5 bg-background border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary/20 transition-all appearance-none"
                >
                  {CITIES.map(c => (
                    <option key={c} value={c}>{c}</option>
                  ))}
                </select>
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full xl:w-auto px-6 py-2.5 bg-primary text-primary-foreground rounded-lg text-sm font-medium hover:bg-primary/90 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 shrink-0 h-[42px]"
            >
              {loading ? (
                <span className="w-4 h-4 border-2 border-primary-foreground/30 border-t-primary-foreground rounded-full animate-spin" />
              ) : (
                <Search className="w-4 h-4" />
              )}
              Tìm kiếm
            </button>
          </div>
        </form>
      </div>

      {error && (
        <div className="p-4 bg-red-500/10 border border-red-500/20 text-red-600 dark:text-red-400 rounded-lg text-sm">
          {error}
        </div>
      )}

      {jobs.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 2xl:grid-cols-3 gap-4">
          {jobs.map((job) => (
            <div key={job.id} className="group bg-card border border-border/50 hover:border-primary/30 rounded-xl p-5 transition-all hover:shadow-md flex flex-col h-full overflow-hidden">
              <div className="flex items-start justify-between gap-3 mb-3 w-full">
                <h3 className="font-semibold text-[15px] leading-tight group-hover:text-primary transition-colors line-clamp-2 flex-1 min-w-0">
                  <a href={job.url} target="_blank" rel="noreferrer" className="flex items-center gap-1.5 hover:underline" title={job.title}>
                    <span className="truncate whitespace-normal line-clamp-2">{job.title}</span>
                    <ExternalLink className="w-3 h-3 opacity-0 group-hover:opacity-100 transition-opacity shrink-0 inline-block" />
                  </a>
                </h3>
                <span className="shrink-0 inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-secondary/50 text-[10px] font-medium text-muted-foreground border border-border/50 whitespace-nowrap">
                  {job.source}
                </span>
              </div>
              
              <div className="flex flex-wrap gap-x-4 gap-y-2 mb-4 text-xs text-muted-foreground">
                <div className="flex items-center gap-1.5 text-foreground/80 min-w-0">
                  <Building2 className="w-3.5 h-3.5 shrink-0" />
                  <span className="font-medium truncate">{job.company}</span>
                </div>
                <div className="flex items-center gap-1.5 min-w-0">
                  <MapPin className="w-3.5 h-3.5 shrink-0" />
                  <span className="truncate">{job.location}</span>
                </div>
                <div className="flex items-center gap-1.5 shrink-0">
                  <Briefcase className="w-3.5 h-3.5 shrink-0" />
                  <span className="capitalize">{job.work_model}</span>
                </div>
              </div>
              
              <div 
                className="text-[13px] text-muted-foreground leading-relaxed line-clamp-3 mb-4 flex-1 break-words"
                dangerouslySetInnerHTML={{ __html: job.description }}
              />

              {job.posted_at && (
                <div className="text-[11px] text-muted-foreground/60 mt-auto pt-4 border-t border-border/30">
                  Đăng lúc: {new Date(job.posted_at).toLocaleDateString("vi-VN")}
                </div>
              )}
            </div>
          ))}
        </div>
      ) : (
        !loading && jobs.length === 0 && !error && (
            <div className="py-20 flex flex-col items-center justify-center text-center bg-card border border-border/50 rounded-xl border-dashed">
              <div className="w-12 h-12 bg-secondary/50 rounded-full flex items-center justify-center mb-4">
                <Briefcase className="w-6 h-6 text-muted-foreground/50" />
              </div>
              <h3 className="text-sm font-medium mb-1">Chưa có kết quả</h3>
              <p className="text-xs text-muted-foreground max-w-sm">
                Hãy nhập vị trí hoặc chọn trình độ và nhấn tìm kiếm để xem các cơ hội việc làm mới nhất.
              </p>
            </div>
        )
      )}
    </div>
  );
}
