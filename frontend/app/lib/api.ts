const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8888/api/v1";

export async function fetchFromAPI(endpoint: string, options: RequestInit = {}) {
    const response = await fetch(`${API_BASE_URL}/${endpoint}`, {
        ...options,
        headers: {
            'Content-Type': 'application/json',
            ...options.headers
        },
    });
    return response.json();
}