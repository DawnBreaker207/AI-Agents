import {fetchFromAPI} from "~/lib/api";
import type {ResearchReport} from "~/types";

const AI_BACKEND_URL = import.meta.env.VITE_API_URL || "http://localhost:8888/api/v1";

export async function generateReport(topic: string) {
    try {
        const response = await fetch(`${AI_BACKEND_URL}/generate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({topic}),
        });

        if (!response.ok) {
            throw new Error(`API call failed with status: ${response.status}`);
        }
        return response.json();
    } catch (error) {
        console.error("Failed to generate report:", error);
        throw error;
    }
}

export async function getReportById(id: string): Promise<ResearchReport | null> {
    try {
        if (!id) return null;
        const data = await fetchFromAPI(`report/${id}`);
        return data as ResearchReport;
    } catch (error) {
        console.error(`Failed to fetch report ${id}:`, error);
        return null;
    }
}

export async function getReports(filters?: {
    search?: string | null;
    category?: string | null
}): Promise<ResearchReport[]> {
    try {
        const queryParams = new URLSearchParams();
        if (filters?.search) queryParams.append("search", filters.search);
        if (filters?.category && filters.category !== "all") queryParams.append("category", filters.category);

        const data = await fetchFromAPI(`history?${queryParams.toString()}`)
        return data as ResearchReport[];
    } catch (error) {
        console.error("Failed to fetch reports:", error);
        return [];
    }
}