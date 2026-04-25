import type {ResearchReport} from "~/types";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8888/api/v1";


export async function getHistory(): Promise<ResearchReport[]> {
    const res = await fetch(`${API_BASE_URL}/agent/history`);
    if (!res.ok) return [];
    return res.json();
}

export async function startResearch(topic: string): Promise<ResearchReport> {
    const res = await fetch(`${API_BASE_URL}/agent/research`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({topic}),
    });
    if (!res.ok) throw new Error("Agent failed");
    return res.json();
}