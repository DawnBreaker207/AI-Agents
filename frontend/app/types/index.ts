export type Sentiment = "Tích cực" | "Tiêu cực" | "Trung tính" | "Không xác định";

export interface TechTrend {
    name: string;
    update: string;
}

export interface ResearchArticle {
    title: string;
    url: string;
}

export interface ResearchReport {
    id: string;
    topic: string;
    title: string;
    summary: string;
    impact_score: number;
    sentiment: Sentiment;
    categories: string[];
    regions: string[];

    tech_trends: TechTrend[];
    employment_status: {
        market: string;
        demand: string;
    };
    job_details: {
        salary: string;
        skills: string[];
    };
    research_articles: ResearchArticle[];

    sources: string[];
    last_updated: string;
    created_at: string;
}