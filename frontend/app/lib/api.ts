import type { ResearchReport, PendingNews, SourceList, TopicWhitelist, FeedMetrics } from "~/types";

export const API_BASE_URL = (typeof process !== "undefined" && process.env?.API_BASE_URL)
  || (typeof import.meta !== "undefined" && import.meta.env?.VITE_API_URL)
  || "http://localhost:8888";

interface ApiResponse<T> {
  message: string;
  data: T;
  timestamp: string;
}

const REQUEST_TIMEOUT = 15_000;

/**
 * Generic fetch wrapper with timeout, auto-unwraps APIResponse envelope.
 */
async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const url = `${API_BASE_URL}${path}`;
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), REQUEST_TIMEOUT);
  try {
    const res = await fetch(url, {
      signal: controller.signal,
      headers: { "Content-Type": "application/json", ...init?.headers },
      ...init,
    });
    if (!res.ok) {
      console.error(`API Error: ${res.status} - ${url}`);
      throw new Error(`API error ${res.status}: ${url}`);
    }
    const json = await res.json();
    if (json && typeof json === "object" && "data" in json && "message" in json) {
      return json.data as T;
    }
    return json as T;
  } finally {
    clearTimeout(timer);
  }
}

/**
 * GET /health - Check agent status
 */
export const getHealth = () =>
  apiFetch<{ status: string; agent: string }>("/health");

/**
 * POST /research - Start research pipeline on a new topic
 */
export const startResearch = (topic: string, force_refresh = false) =>
  apiFetch<{ status: string; topic: string }>("/research", {
    method: "POST",
    body: JSON.stringify({ topic, force_refresh }),
  });

/**
 * POST /chat - Chat with the AI Analyst agent
 */
export const chatWithAgent = (prompt: string, category = "all") =>
  apiFetch<{ answer: string }>("/chat", {
    method: "POST",
    body: JSON.stringify({ prompt, category }),
  });

/**
 * GET /api/news/:status - Get news filtered by status with pagination
 */
export const getNewsByStatus = (status: string, page = 1, size = 20) =>
  apiFetch<PendingNews[]>(`/api/news/${status.toLowerCase()}?page=${page}&size=${size}`);

/**
 * GET /api/news/watch - Get watchlist news
 */
export const getWatchNews = (category?: string, page = 1, size = 20) => {
  const q = new URLSearchParams({ page: String(page), size: String(size) });
  if (category) q.set("category", category);
  return apiFetch<PendingNews[]>(`/api/news/watch?${q}`);
};

/**
 * POST /api/news/:id/promote - Promote news to KEEP status manually
 */
export const promoteNews = (newsId: number) =>
  apiFetch<{ news_id: number; status: string }>(`/api/news/${newsId}/promote`, { method: "POST" });

/**
 * POST /api/research/:id - Trigger deep analysis (Stage 3) on news
 */
export const triggerDeepAnalysis = (newsId: number) =>
  apiFetch<{ status: string }>(`/api/research/${newsId}`, { method: "POST" });

/**
 * GET /history - Get research reports history with search and category filters
 */
export const getReportHistory = (search?: string, category?: string) => {
  const params = new URLSearchParams();
  if (search) params.append("search", search);
  if (category && category !== "all") params.append("category", category);
  const qs = params.toString();
  return apiFetch<ResearchReport[]>(`/history${qs ? `?${qs}` : ""}`);
};

/**
 * GET /api/reports/:id - Get a report by its ID (includes source_citations, citation_count)
 * This is the CORRECT, verified endpoint with full citation data.
 */
export const getReportById = (id: string | number) =>
  apiFetch<ResearchReport>(`/api/reports/${id}`);

/**
 * GET /api/reports/strategic - Get strategic research reports
 */
export const getStrategicReports = () =>
  apiFetch<ResearchReport[]>("/api/reports/strategic");

/**
 * GET /api/sources - Get RSS feed sources
 */
export const getSources = () =>
  apiFetch<SourceList[]>("/api/sources");

/**
 * PUT /api/sources/:id/toggle - Toggle RSS source active state
 */
export const toggleSource = (sourceId: number) =>
  apiFetch<{ id: number; is_active: boolean }>(`/api/sources/${sourceId}/toggle`, { method: "PUT" });

/**
 * GET /api/whitelist - Get Whitelist topics
 */
export const getWhitelist = () =>
  apiFetch<TopicWhitelist[]>("/api/whitelist");

/**
 * POST /api/whitelist - Add new topic to Whitelist
 */
export const addWhitelistTopic = (topic: string, boost_score: number, force_keep: boolean) =>
  apiFetch<{ status: string; topic: string }>("/api/whitelist", {
    method: "POST",
    body: JSON.stringify({ topic, boost_score, force_keep }),
  });

/**
 * DELETE /api/whitelist/:id - Delete topic from Whitelist by ID
 */
export const deleteWhitelistTopic = (topicId: number) =>
  apiFetch<{ status: string }>(`/api/whitelist/${topicId}`, { method: "DELETE" });

/**
 * GET /api/metrics - Get overview metrics
 */
export const getFeedMetrics = () =>
  apiFetch<FeedMetrics>("/api/metrics");

/**
 * POST /api/pipeline/trigger - Manually trigger the scraping pipeline
 */
export const triggerPipeline = () =>
  apiFetch<{ status: string; message: string }>("/api/pipeline/trigger", { method: "POST" });

/**
 * POST /api/pipeline/translate - Batch translate existing English titles to Vietnamese
 */
export const translateTitles = () =>
  apiFetch<{ status: string; message: string }>("/api/pipeline/translate", { method: "POST" });

// ── Job Watch API ──────────────────────────────────────────────────────────

export interface JobWatchItem {
  id: number;
  position: string;
  level: string;
  location_type: string;
  city: string;
  created_at: string | null;
}

export interface JobResult {
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
  salary: string;
  tags: string[];
}

export const getJobWatches = () =>
  apiFetch<JobWatchItem[]>("/api/jobs/watch");

export const addJobWatch = (position: string, level: string, location_type: string, city: string) => {
  const params = new URLSearchParams({ position, level, location_type, city });
  return apiFetch<JobWatchItem>(`/api/jobs/watch?${params}`, { method: "POST" });
};

export const deleteJobWatch = (watchId: number) =>
  apiFetch<{ id: number }>(`/api/jobs/watch/${watchId}`, { method: "DELETE" });

export const searchJobs = (keyword: string, location_type: string, level: string, city: string) => {
  const params = new URLSearchParams({ keyword, location_type, level, city });
  return apiFetch<JobResult[]>(`/api/jobs/search?${params}`);
};