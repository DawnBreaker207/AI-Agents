import { Form, Link, useNavigation } from "react-router";
import { Search, Briefcase, MapPin, Globe, Building2, ExternalLink } from "lucide-react";
import type { Route } from "./+types/jobs";
import { searchJobs } from "~/lib/api";
import type { JobResult } from "~/lib/api";
import { useState } from "react";

const LEVELS = ["Tất cả", "Intern", "Junior", "Middle", "Senior", "Lead / Principal"];
const CITIES = ["Tất cả", "Hà Nội", "Hồ Chí Minh", "Đà Nẵng", "Khác"];

export async function loader({ request }: Route.LoaderArgs) {
  const url = new URL(request.url);
  const keyword = url.searchParams.get("keyword") ?? "";
  const level = url.searchParams.get("level") ?? "Tất cả";
  const locationType = url.searchParams.get("location_type") ?? "domestic";
  const city = url.searchParams.get("city") ?? "Tất cả";

  if (!keyword && level === "Tất cả") {
    return { keyword, level, locationType, city, jobs: [] as JobResult[] };
  }

  try {
    const data = await searchJobs(keyword, locationType, level, city);
    return { keyword, level, locationType, city, jobs: Array.isArray(data) ? data : [] };
  } catch {
    return { keyword, level, locationType, city, jobs: [] as JobResult[] };
  }
}

export default function JobsPage({ loaderData }: Route.ComponentProps) {
  const { jobs, keyword, level, locationType, city } = loaderData;
  const navigation = useNavigation();
  const isLoading = navigation.state !== "idle"
    && navigation.location?.pathname === "/jobs";
  const [locUI, setLocUI] = useState(locationType);

  return (
    <div className="flex flex-col gap-6 w-full h-full pb-10">
      <div className="flex flex-col gap-2">
        <h1 className="text-2xl font-medium tracking-tight">Tìm Kiếm Việc Làm</h1>
        <p className="text-sm text-muted-foreground">
          Khám phá cơ hội nghề nghiệp từ các nguồn uy tín. Hỗ trợ tìm việc trực tiếp trong nước và việc làm từ xa quốc tế.
        </p>
      </div>

      <div className="bg-card border border-border/50 rounded-xl p-5">
        <Form method="get" className="flex flex-col gap-4">
          <div className="flex flex-col xl:flex-row gap-4 items-end">

            <div className="flex-1 w-full space-y-1.5 min-w-[200px]">
              <label htmlFor="job-keyword" className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Vị trí tuyển dụng (VD: React, Python...)</label>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                <input
                  id="job-keyword"
                  name="keyword"
                  type="text"
                  defaultValue={keyword}
                  placeholder="VD: Frontend, React, Python, VNG..."
                  className="w-full pl-9 pr-4 py-3 bg-background border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary/20 motion-safe:transition-colors min-h-11"
                />
              </div>
            </div>

            <div className="w-full xl:w-48 space-y-1.5 shrink-0">
              <label htmlFor="job-level" className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Trình độ / Level</label>
              <select
                id="job-level"
                name="level"
                defaultValue={level}
                className="w-full px-3 py-3 bg-background border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary/20 motion-safe:transition-colors appearance-none min-h-11"
              >
                {LEVELS.map(l => (
                  <option key={l} value={l}>{l}</option>
                ))}
              </select>
            </div>

            <div className="w-full xl:w-64 space-y-1.5 shrink-0">
              <label className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Loại việc làm</label>
              <div className="flex bg-background border border-border rounded-lg overflow-hidden p-1">
                {(["domestic", "overseas"] as const).map(t => (
                  <label
                    key={t}
                    className={`flex-1 flex items-center justify-center gap-1.5 py-2 text-xs font-medium rounded-md motion-safe:transition-colors cursor-pointer ${
                      locUI === t ? "bg-primary text-primary-foreground" : "text-muted-foreground hover:bg-secondary/50"
                    }`}
                  >
                    <input
                      type="radio"
                      name="location_type"
                      value={t}
                      defaultChecked={locationType === t}
                      onChange={(e) => setLocUI(e.target.value)}
                      className="sr-only"
                    />
                    {t === "domestic" ? <MapPin className="w-3.5 h-3.5" /> : <Globe className="w-3.5 h-3.5" />}
                    {t === "domestic" ? "Trong nước" : "Quốc tế"}
                  </label>
                ))}
              </div>
            </div>

            {locUI === "domestic" && (
              <div className="w-full xl:w-40 space-y-1.5 shrink-0">
                <label htmlFor="job-city" className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Thành phố</label>
                <select
                  id="job-city"
                  name="city"
                  defaultValue={city}
                  className="w-full px-3 py-3 bg-background border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary/20 motion-safe:transition-colors appearance-none min-h-11"
                >
                  {CITIES.map(c => (
                    <option key={c} value={c}>{c}</option>
                  ))}
                </select>
              </div>
            )}

            <button
              type="submit"
              disabled={isLoading}
              className="w-full xl:w-auto px-6 py-3 bg-primary text-primary-foreground rounded-lg text-sm font-medium hover:bg-primary/90 motion-safe:transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 shrink-0 min-h-11"
            >
              {isLoading ? (
                <span className="w-4 h-4 border-2 border-primary-foreground/30 border-t-primary-foreground rounded-full motion-safe:animate-spin" />
              ) : (
                <Search className="w-4 h-4" />
              )}
              Tìm kiếm
            </button>
          </div>
        </Form>
      </div>

      {jobs.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 2xl:grid-cols-3 gap-4">
          {jobs.map((job) => (
            <div key={job.id} className="group bg-card border border-border/50 hover:border-primary/30 rounded-xl p-5 motion-safe:transition-colors hover:bg-muted/20 flex flex-col h-full overflow-hidden">
              <div className="flex items-start justify-between gap-3 mb-3 w-full">
                <h2 className="font-medium text-[15px] leading-tight group-hover:text-primary motion-safe:transition-colors line-clamp-2 flex-1 min-w-0">
                  <a href={job.url} target="_blank" rel="noreferrer" className="flex items-center gap-1.5 hover:underline" title={job.title}>
                    <span className="truncate whitespace-normal line-clamp-2">{job.title}</span>
                    <ExternalLink className="w-3 h-3 opacity-0 group-hover:opacity-100 transition-opacity shrink-0 inline-block" />
                  </a>
                </h2>
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

              <p className="text-[13px] text-muted-foreground leading-relaxed line-clamp-3 mb-4 flex-1 break-words">{job.description}</p>

              {job.posted_at && (
                <div className="text-[11px] text-muted-foreground/60 mt-auto pt-4 border-t border-border/30">
                  Đăng lúc: {new Date(job.posted_at).toLocaleDateString("vi-VN")}
                </div>
              )}
            </div>
          ))}
        </div>
      ) : (
        !isLoading && (
          <div className="py-20 flex flex-col items-center justify-center text-center bg-card border border-border/50 rounded-xl border-dashed">
            <div className="w-12 h-12 bg-secondary/50 rounded-full flex items-center justify-center mb-4">
              <Briefcase className="w-6 h-6 text-muted-foreground/50" />
            </div>
            <h2 className="text-sm font-medium mb-1">Chưa có kết quả</h2>
            <p className="text-xs text-muted-foreground max-w-sm">
              Hãy nhập vị trí hoặc chọn trình độ và nhấn tìm kiếm để xem các cơ hội việc làm mới nhất.
            </p>
          </div>
        )
      )}
    </div>
  );
}
