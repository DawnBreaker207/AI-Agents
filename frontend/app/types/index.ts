export type Sentiment = "Tích cực" | "Tiêu cực" | "Trung tính" | "Không xác định" | "POSITIVE" | "NEUTRAL" | "NEGATIVE";

export interface TechTrend {
    name: string;
    update: string;
}

export interface ResearchArticle {
    title: string;
    url: string;
}

export interface ResearchReport {
    id: number;
    pending_news_id?: number | null;
    title: string;
    original_source?: string | null;
    // Danh sách link dẫn chứng đã xác minh (bắt buộc phải tồn tại & đúng nguồn)
    source_citations?: string[] | null;
    citation_count?: number | null;
    executive_summary?: string | null;
    technical_deep_dive?: string | null;
    vietnam_market_impact?: string | null;
    strategic_action_items?: string[] | null;
    impact_score: number;
    sentiment: Sentiment;
    category?: string | null;  // category thật từ Gatekeeper (2.2)
    tags?: string[] | null;
    created_at: string;

    // Legacy fields for backward compatibility
    topic?: string;
    summary?: string;
    categories?: string[];
    regions?: string[];
    tech_trends?: TechTrend[];
    employment_status?: {
        market: string;
        demand: string;
    };
    job_details?: {
        salary: string;
        skills: string[];
    };
    research_articles?: ResearchArticle[];
    sources?: string[];
    last_updated?: string;
}

export type NewsStatus =
  | "PENDING" | "WATCH" | "KEEP" | "KEEP_URGENT" | "TRASH" | "PROCESSED";

export type NewsCategory =
  | "AI_RESEARCH" | "LAYOFF" | "VN_MARKET"
  | "DEV_TOOLS" | "SECURITY" | "BUSINESS" | "OTHER";

export interface PendingNews {
  id:             number;
  title:          string;
  snippet:        string | null;
  url:            string;
  source_domain:  string | null;
  published_at:   string | null;   // chuỗi ISO
  status:         NewsStatus;
  impact_score:   number | null;
  category:       NewsCategory | null;
  matched_topics: string[] | null;
}

export interface SourceList {
  id:              number;
  name:            string;
  url:             string;
  type:            "RSS" | "SCRAPE";
  is_active:       boolean;
  priority_weight: number;
}

export interface TopicWhitelist {
  id:          number;
  topic:       string;
  boost_score: number;
  force_keep:  boolean;
  is_active:   boolean;
}

export interface FeedMetrics {
  total_today: number;
  keep_urgent: number;
  keep:        number;
  watch:       number;
  trash:       number;
  processed:   number;
  last_run_at: string | null;
}