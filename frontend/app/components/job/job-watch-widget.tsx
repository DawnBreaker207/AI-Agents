import { useState } from "react";
import { Link, useFetcher } from "react-router";
import { Briefcase, Plus, Trash2, MapPin, Globe, ExternalLink, Loader2 } from "lucide-react";
import { searchJobs } from "~/lib/api";
import type { JobWatchItem, JobResult } from "~/lib/api";
import { toast } from "sonner";

const LEVELS = ["Tất cả", "Intern", "Junior", "Middle", "Senior", "Lead / Principal"];
const CITIES = ["Tất cả", "Hà Nội", "Hồ Chí Minh", "Đà Nẵng"];

interface JobWatchWidgetProps {
  watches: JobWatchItem[];
}

export default function JobWatchWidget({ watches }: JobWatchWidgetProps) {
  const [activeWatch, setActiveWatch] = useState<JobWatchItem | null>(null);
  const [results, setResults] = useState<JobResult[]>([]);
  const [loadingSearch, setLoadingSearch] = useState(false);

  // Add form state
  const [showAdd, setShowAdd] = useState(false);
  const [newPos, setNewPos] = useState("");
  const [newLevel, setNewLevel] = useState("Tất cả");
  const [newLocType, setNewLocType] = useState<"domestic" | "overseas">("domestic");
  const [newCity, setNewCity] = useState("Tất cả");

  const addFetcher = useFetcher();
  const deleteFetcher = useFetcher();

  const handleAdd = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newPos.trim()) return;
    addFetcher.submit(
      { intent: "addWatch", position: newPos, level: newLevel, location_type: newLocType, city: newCity },
      { method: "post", action: "/dashboard" }
    );
    setNewPos("");
    setNewLevel("Tất cả");
    setNewCity("Tất cả");
    setShowAdd(false);
    toast.success("Đã thêm vị trí theo dõi");
  };

  const handleDelete = (w: JobWatchItem) => {
    deleteFetcher.submit(
      { intent: "deleteWatch", watchId: String(w.id) },
      { method: "post", action: "/dashboard" }
    );
    if (activeWatch?.id === w.id) {
      setActiveWatch(null);
      setResults([]);
    }
    toast.success("Đã xóa vị trí theo dõi");
  };

  const handleSelect = async (w: JobWatchItem) => {
    setActiveWatch(w);
    setLoadingSearch(true);
    setResults([]);
    try {
      const data = await searchJobs(w.position, w.location_type, w.level, w.city);
      setResults(Array.isArray(data) ? data : []);
    } catch {
      toast.error("Không thể tải kết quả tìm kiếm");
    } finally {
      setLoadingSearch(false);
    }
  };

  return (
    <div className="flex flex-col gap-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Briefcase className="w-4 h-4 text-primary" />
          <h2 className="text-sm font-medium text-foreground">Vị trí việc làm quan tâm</h2>
        </div>
        <button
          onClick={() => setShowAdd(v => !v)}
          className="flex items-center gap-1 text-[11px] font-medium text-primary border border-primary/30 rounded-full px-3 py-1.5 hover:bg-primary/10 motion-safe:transition-colors min-h-11"
          aria-label="Thêm vị trí việc làm theo dõi"
        >
          <Plus className="w-3 h-3" />
          Thêm vị trí
        </button>
      </div>

      {/* Add form */}
      {showAdd && (
        <form onSubmit={handleAdd} className="bg-muted/30 border border-border/50 rounded-xl p-4 flex flex-col gap-3">
          <div className="flex flex-wrap gap-3">
            <label htmlFor="new-watch-position" className="sr-only">Vị trí tuyển dụng</label>
            <input
              id="new-watch-position"
              value={newPos}
              onChange={e => setNewPos(e.target.value)}
              placeholder="Vị trí (VD: React, Java, Data Engineer...)"
              required
              className="flex-1 min-w-[180px] px-3 py-3 bg-background border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary/20 min-h-11"
            />
            <label htmlFor="new-watch-level" className="sr-only">Trình độ</label>
            <select
              id="new-watch-level"
              value={newLevel}
              onChange={e => setNewLevel(e.target.value)}
              className="px-3 py-3 bg-background border border-border rounded-lg text-sm focus:outline-none min-h-11"
            >
              {LEVELS.map(l => <option key={l} value={l}>{l}</option>)}
            </select>
            <div className="flex bg-background border border-border rounded-lg overflow-hidden">
              {(["domestic", "overseas"] as const).map(t => (
                <button
                  key={t}
                  type="button"
                  onClick={() => setNewLocType(t)}
                  className={`px-3 py-2 text-xs font-medium flex items-center gap-1 motion-safe:transition-colors ${
                    newLocType === t ? "bg-primary text-primary-foreground" : "text-muted-foreground hover:bg-secondary/50"
                  }`}
                  aria-pressed={newLocType === t}
                >
                  {t === "domestic" ? <MapPin className="w-3 h-3" /> : <Globe className="w-3 h-3" />}
                  {t === "domestic" ? "Trong nước" : "Quốc tế"}
                </button>
              ))}
            </div>
            {newLocType === "domestic" && (
              <>
                <label htmlFor="new-watch-city" className="sr-only">Thành phố</label>
                <select
                  id="new-watch-city"
                  value={newCity}
                  onChange={e => setNewCity(e.target.value)}
                  className="px-3 py-3 bg-background border border-border rounded-lg text-sm focus:outline-none min-h-11"
                >
                  {CITIES.map(c => <option key={c} value={c}>{c}</option>)}
                </select>
              </>
            )}
          </div>
          <div className="flex gap-2 justify-end">
            <button type="button" onClick={() => setShowAdd(false)} className="px-4 py-2.5 text-xs text-muted-foreground border border-border rounded-lg hover:bg-muted/50 min-h-11" aria-label="Hủy thêm vị trí">
              Hủy
            </button>
            <button type="submit" disabled={addFetcher.state !== "idle"} className="px-5 py-2.5 text-xs font-medium bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 disabled:opacity-50 flex items-center gap-1.5 min-h-11">
              {addFetcher.state !== "idle" && <Loader2 className="w-3 h-3 motion-safe:animate-spin" />}
              Lưu
            </button>
          </div>
        </form>
      )}

      {/* Watch list + results */}
      <div className="flex gap-4 flex-col lg:flex-row">
        {/* Watch chips */}
        <div className="flex flex-wrap gap-2 lg:flex-col lg:w-56 lg:shrink-0">
          {watches.length === 0 && (
            <p className="text-xs text-muted-foreground/60 italic py-2">
              Chưa có vị trí nào được theo dõi.
            </p>
          )}
          {watches.map(w => (
            <button
              key={w.id}
              onClick={() => handleSelect(w)}
              className={`group flex items-center gap-2 text-left rounded-xl px-3 py-2.5 border motion-safe:transition-colors text-[12px] w-full ${
                activeWatch?.id === w.id
                  ? "bg-primary/10 border-primary/40 text-primary"
                  : "bg-card border-border/50 hover:border-primary/30 text-foreground"
              }`}
            >
              <div className="flex-1 min-w-0">
                <p className="font-medium truncate">{w.position}</p>
                <p className="text-muted-foreground text-[10px] flex items-center gap-1">
                  {w.location_type === "domestic" ? <MapPin className="w-2.5 h-2.5 shrink-0" /> : <Globe className="w-2.5 h-2.5 shrink-0" />}
                  {w.level !== "Tất cả" ? `${w.level} · ` : ""}{w.location_type === "domestic" ? (w.city !== "Tất cả" ? w.city : "Việt Nam") : "Remote"}
                </p>
              </div>
              <button
                onClick={e => { e.stopPropagation(); handleDelete(w); }}
                className="opacity-0 group-hover:opacity-100 p-1.5 rounded-md hover:bg-destructive/10 text-muted-foreground/60 hover:text-destructive motion-safe:transition-colors shrink-0 min-h-11 min-w-11 flex items-center justify-center"
                aria-label={`Xóa theo dõi ${w.position}`}
              >
                <Trash2 className="w-3 h-3" />
              </button>
            </button>
          ))}
          {watches.length > 0 && (
            <Link
              to="/jobs"
              className="text-[11px] text-primary hover:underline font-medium px-3 py-1.5 flex items-center gap-1"
            >
              Tìm kiếm nâng cao <ExternalLink className="w-3 h-3" />
            </Link>
          )}
        </div>

        {/* Results panel */}
        {activeWatch && (
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-3">
              <p className="text-[12px] font-medium text-foreground">
                Kết quả cho <span className="text-primary">{activeWatch.position}</span>
                {activeWatch.level !== "Tất cả" && <span className="text-muted-foreground"> · {activeWatch.level}</span>}
              </p>
              {loadingSearch && <Loader2 className="w-3.5 h-3.5 motion-safe:animate-spin text-muted-foreground" />}
            </div>

            {!loadingSearch && results.length === 0 && (
              <p className="text-xs text-muted-foreground/60 italic">Không tìm thấy kết quả.</p>
            )}

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {results.slice(0, 6).map(job => (
                <a
                  key={job.id}
                  href={job.url}
                  target="_blank"
                  rel="noreferrer"
                  className="group block bg-card border border-border/50 hover:border-primary/30 rounded-xl p-3.5 motion-safe:transition-colors hover:bg-muted/20"
                >
                  <div className="flex items-start justify-between gap-2 mb-2">
                    <p className="text-[13px] font-medium leading-snug group-hover:text-primary motion-safe:transition-colors line-clamp-2 flex-1">
                      {job.title}
                    </p>
                    <span className="shrink-0 text-[9px] font-medium px-1.5 py-0.5 rounded-full bg-secondary/50 text-muted-foreground border border-border/50 whitespace-nowrap">
                      {job.source}
                    </span>
                  </div>
                  {job.company && (
                    <p className="text-[11px] text-muted-foreground mb-1.5 font-medium">{job.company}</p>
                  )}
                  <p className="text-[11px] text-muted-foreground line-clamp-2 leading-relaxed">{job.description}</p>
                  {job.salary && (
                    <p className="mt-1.5 text-[11px] text-green-600 dark:text-green-400 font-medium">{job.salary}</p>
                  )}
                </a>
              ))}
            </div>

            {results.length > 6 && (
              <div className="mt-3 text-center">
                <Link
                  to={`/jobs?keyword=${encodeURIComponent(activeWatch.position)}&location_type=${activeWatch.location_type}&level=${encodeURIComponent(activeWatch.level)}&city=${encodeURIComponent(activeWatch.city)}`}
                  className="text-[11px] font-medium text-primary hover:underline"
                >
                  Xem tất cả {results.length} kết quả →
                </Link>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
