import type {ResearchReport} from "~/types";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8888/api/v1";

export async function fetchFromAPI<T>(endpoint: string, options: RequestInit = {}): Promise<T> {

    const url = `${API_BASE_URL}/${endpoint}`;
    const response = await fetch(url, {
        ...options,
        headers: {
            'Content-Type': 'application/json',
            ...options.headers
        },
    });
    if (!response.ok) {
        console.error(`❌ API Error: ${response.status} - ${url}`);
        throw new Error(`API Error: ${response.statusText}`);
    }
    return response.json();
}

export const agentApi = {
    getSignals: () =>
        fetchFromAPI<any>('signals'),
    // Bắt đầu nghiên cứu mới hoặc lấy từ cache
    startResearch: (topic: string, refresh: boolean) =>
        fetchFromAPI<ResearchReport>('research', {
            method: 'POST',
            body: JSON.stringify({
                topic: topic,
                force_refresh: refresh
            })
        }),

    // Lấy lịch sử
    getHistory: (search?: string, category?: string) => {
        const params = new URLSearchParams();
        if (search) params.append("search", search);
        if (category && category !== "all") params.append("category", category);

        // Endpoint khớp với @agent_router.get("/history")
        return fetchFromAPI<ResearchReport[]>(`history?${params.toString()}`);
    },

    chat: (prompt: string, category: string = "all") =>
        fetchFromAPI<{ answer: string }>('chat', {
            method: 'POST',
            body: JSON.stringify({prompt, category})
        }),

    // Lấy chi tiết 1 báo cáo
    getReportById: (id: string | number) =>
        fetchFromAPI<ResearchReport>(`report/${id}`),
};