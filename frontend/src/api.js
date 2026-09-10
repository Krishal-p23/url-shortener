const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json", ...options.headers },
    ...options,
  });

  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail || "The request could not be completed.");
  }
  return response.json();
}

export function shortenUrl(url) {
  return request("/api/v1/urls", {
    method: "POST",
    body: JSON.stringify({ url }),
  });
}

export function getAnalytics(shortCode) {
  return request(`/api/v1/urls/${encodeURIComponent(shortCode)}/analytics`);
}