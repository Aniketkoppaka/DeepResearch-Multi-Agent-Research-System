import { CITATIONS, METRICS, PLAN, REPORT, SESSIONS } from "./research-data";
import type { Citation, Metrics, Plan, ResearchMode, Session } from "./research-data";

const BASE = "/api/v1";

function getAuthHeader(): Record<string, string> {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("access_token");
    if (token) return { Authorization: `Bearer ${token}` };
  }
  return {};
}

async function request<T>(path: string, init: RequestInit, fallback: T): Promise<T> {
  try {
    const res = await fetch(`${BASE}${path}`, {
      headers: {
        "Content-Type": "application/json",
        ...getAuthHeader(),
        ...init.headers,
      },
      ...init,
    });
    if (!res.ok) throw new Error(String(res.status));
    return (await res.json()) as T;
  } catch {
    await new Promise((r) => setTimeout(r, 200));
    return fallback;
  }
}

export const researchApi = {
  login: (email: string, password: string) =>
    request(`/auth/login`, { method: "POST", body: JSON.stringify({ email, password }) }, { ok: true }),
  register: (email: string, password: string) =>
    request(`/auth/register`, { method: "POST", body: JSON.stringify({ email, password }) }, { ok: true }),
  listWorkspaces: () => request<Session[]>(`/workspaces`, { method: "GET" }, SESSIONS),
  createWorkspace: (title: string, mode: ResearchMode) =>
    request<Session>(`/workspaces`, { method: "POST", body: JSON.stringify({ title, mode }) }, {
      id: `w-${Date.now()}`,
      title,
      mode,
      group: "Today" as const,
    }),
  generatePlan: (id: string, brief: string) =>
    request<Plan>(`/workspaces/${id}/plan/generate`, { method: "POST", body: JSON.stringify({ user_feedback: brief }) }, PLAN),
  reviewPlan: (id: string, approved: boolean, feedback?: string) =>
    request(`/workspaces/${id}/plan/review`, { method: "POST", body: JSON.stringify({ approved, feedback }) }, { ok: true }),
  execute: (id: string) =>
    request<{ report: string; citations: Citation[] }>(`/workspaces/${id}/execute`, { method: "POST" }, {
      report: REPORT,
      citations: CITATIONS,
    }),
  latestReport: (id: string) =>
    request<{ report: string; citations: Citation[] }>(`/workspaces/${id}/reports/latest`, { method: "GET" }, {
      report: REPORT,
      citations: CITATIONS,
    }),
  exportUrl: (id: string, format: "markdown" | "html" | "pdf") =>
    `/api/v1/workspaces/${id}/export?format=${format}`,
  metrics: (id: string) => request<Metrics>(`/workspaces/${id}/metrics`, { method: "GET" }, METRICS),
};
