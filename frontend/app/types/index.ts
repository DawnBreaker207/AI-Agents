export type Sentiment = "Tích cực" | "Tiêu cực" | "Trung tính" | "Không xác định";

export interface ResearchReport {
    id: number;
    title: string;
    summary?: string;
    key_points: string[];
    sentiment: Sentiment;
    sources: string[];
    created_at: string;
    categories: string[];
    regions: string[];
}