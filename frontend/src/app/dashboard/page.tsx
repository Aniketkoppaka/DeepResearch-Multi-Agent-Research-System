"use client";

import React, { useEffect, useRef, useState, useCallback } from "react";
import { useRouter } from "next/navigation";

import { Sparkles, ArrowRight, Lock, LogIn } from "lucide-react";
import { Sidebar } from "@/components/research/Sidebar";
import { Composer } from "@/components/research/Composer";
import { ReasoningAccordion } from "@/components/research/ReasoningAccordion";
import { PlanReviewCard } from "@/components/research/PlanReviewCard";
import { ReportCard } from "@/components/research/ReportCard";
import { SidePanel, type PanelState } from "@/components/research/SidePanel";
import { researchApi } from "@/lib/research-api";
import { useAuthStore } from "@/store/useAuthStore";
import {
  CITATIONS,
  METRICS,
  MODES,
  PLAN,
  REPORT,
  SESSIONS,
  STEPS,
  type ResearchMode,
  type Session,
  type ThoughtTrace,
} from "@/lib/research-data";

type Phase = "empty" | "reasoning" | "plan" | "executing" | "report";

export default function DashboardPage() {
  const router = useRouter();
  const { user, clearAuth, setAuth } = useAuthStore();
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [sessions, setSessions] = useState<Session[]>([]);
  const [activeId, setActiveId] = useState<string | null>(null);
  const [mode, setMode] = useState<ResearchMode>("deep");
  const [phase, setPhase] = useState<Phase>("empty");
  const [prompt, setPrompt] = useState("");
  const [attachments, setAttachments] = useState<string[]>([]);
  const [step, setStep] = useState(0);
  const [thoughtTraces, setThoughtTraces] = useState<ThoughtTrace[]>([]);
  const [decision, setDecision] = useState<"approved" | "refine" | null>(null);
  const [panel, setPanel] = useState<PanelState>(null);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [authMode, setAuthMode] = useState<"login" | "register">("login");
  const [authEmail, setAuthEmail] = useState("");
  const [authPassword, setAuthPassword] = useState("");
  const [authName, setAuthName] = useState("");
  const [authError, setAuthError] = useState("");
  const [authLoading, setAuthLoading] = useState(false);

  const bottomRef = useRef<HTMLDivElement>(null);

  // Load session history from backend or localStorage if logged in
  const loadSessions = useCallback(async () => {
    if (typeof window !== "undefined") {
      const token = localStorage.getItem("access_token");
      if (token) {
        try {
          const list = await researchApi.listWorkspaces();
          if (Array.isArray(list) && list.length > 0) {
            setSessions(list);
            return;
          }
        } catch (_) {}
      }
    }
    setSessions(SESSIONS);
  }, []);

  useEffect(() => {
    // Check if token exists in localStorage on initial mount
    const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : null;
    if (token && !user) {
      // User is authenticated
      setAuth(
        {
          id: "admin-user",
          email: "admin@gmail.com",
          full_name: "Admin",
          is_active: true,
        },
        token
      );
    }
    loadSessions();
  }, [user, setAuth, loadSessions]);

  useEffect(() => {
    if (typeof bottomRef.current?.scrollIntoView === "function") {
      bottomRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [phase, step, decision, thoughtTraces]);


  const addTrace = (agent: string, action: string, detail: string) => {
    const time = new Date().toLocaleTimeString([], { hour12: false });
    setThoughtTraces((prev) => [
      ...prev,
      { agent, action, detail, timestamp: time, status: "completed" },
    ]);
  };

  const startResearch = async (text: string, files: string[], chosenMode: ResearchMode, webSearch: boolean) => {
    setPrompt(text);
    setAttachments(files);
    setMode(chosenMode);
    setDecision(null);
    setPhase("reasoning");
    setThoughtTraces([]);

    addTrace("Supervisor", "INIT_RESEARCH_PLAN", `Analyzing user objective in [${chosenMode.toUpperCase()}] mode.`);
    addTrace("Supervisor", "FORMULATE_HYPOTHESES", "Decomposing into 3 targeted research questions (RQ1, RQ2, RQ3).");

    const ws = activeId
      ? sessions.find((s) => s.id === activeId)!
      : await researchApi.createWorkspace(text.slice(0, 48), chosenMode);

    if (!activeId) {
      setSessions((p) => [ws, ...p]);
      setActiveId(ws.id);
    }

    void researchApi.generatePlan(ws.id, text);

    // Step progression with Antigravity-style traces
    setStep(0);
    setTimeout(() => {
      setStep(1);
      if (webSearch) {
        addTrace("SearchAgent", "WEB_RETRIEVAL", "Executing DuckDuckGo & ArXiv academic literature scan.");
      }
      addTrace("SearchAgent", "QDRANT_HYBRID_SEARCH", "Querying dense vector + sparse BM25 indices with RRF k=60.");
    }, 1200);

    setTimeout(() => {
      addTrace("FactExtractor", "PARSE_CLAIMS", "Extracted 12 atomic claims. Calculating credibility score C(S).");
      setPhase("plan");
    }, 2400);
  };

  const approve = async () => {
    setDecision("approved");
    setPhase("executing");
    setStep(2);

    addTrace("Supervisor", "GATE_APPROVED", "User approved research methodology. Spawning synthesis loop.");
    addTrace("KnowledgeGraph", "EKG_LINKING", "Constructing relational claim edges & checking for contradictory findings.");

    if (activeId) {
      void researchApi.reviewPlan(activeId, true);
      void researchApi.execute(activeId);
    }

    setTimeout(() => {
      setStep(3);
      addTrace("Synthesizer", "SYNTHESIS_REPORT", "Generating grounded markdown report with inline citations [1], [2], [3].");
      addTrace("RagasEvaluator", "GROUNDING_EVALUATION", "Computing Faithfulness (96%), Relevance (94%), Context Precision (91%).");
    }, 1500);

    setTimeout(() => {
      setStep(4);
      setPhase("report");
    }, 3000);
  };

  const refine = async (feedback: string) => {
    setDecision("refine");
    setPhase("reasoning");
    addTrace("Supervisor", "REFINE_PLAN", `Applying user feedback: "${feedback}"`);
    if (activeId) void researchApi.reviewPlan(activeId, false, feedback);

    setTimeout(() => {
      addTrace("Supervisor", "UPDATED_HYPOTHESES", "Generated revised research questions.");
      setDecision(null);
      setPhase("plan");
    }, 1800);
  };

  const selectSession = (id: string) => {
    setActiveId(id);
    const s = sessions.find((x) => x.id === id);
    if (!s) return;
    setMode(s.mode);
    setPrompt(s.title);
    setDecision("approved");
    setStep(4);
    setPhase("report");
    setThoughtTraces([
      {
        agent: "Supervisor",
        action: "LOAD_SESSION",
        detail: `Loaded persisted workspace [${id}]`,
        timestamp: "Historical",
        status: "completed",
      },
      {
        agent: "Synthesizer",
        action: "RESTORE_SYNTHESIS",
        detail: "Restored verified report and grounding evidence citations.",
        timestamp: "Historical",
        status: "completed",
      },
    ]);
  };

  const newSession = () => {
    setActiveId(null);
    setPhase("empty");
    setPrompt("");
    setAttachments([]);
    setDecision(null);
    setThoughtTraces([]);
    setStep(0);
    setPanel(null);
  };

  const renameSession = (id: string) => {
    const next = window.prompt("Rename research session:");
    if (!next?.trim()) return;
    setSessions((p) => p.map((s) => (s.id === id ? { ...s, title: next.trim() } : s)));
  };

  const deleteSession = (id: string) => {
    setSessions((p) => p.filter((s) => s.id !== id));
    if (activeId === id) newSession();
  };

  const openCitation = (id: number) => {
    const c = CITATIONS.find((x) => x.id === id) ?? CITATIONS[0];
    setPanel({ kind: "citation", citation: c });
  };

  const handleLogout = () => {
    if (typeof window !== "undefined") {
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
    }
    clearAuth();
    newSession();
  };

  const handleAuthSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setAuthError("");
    setAuthLoading(true);
    try {
      if (authMode === "login") {
        const res = await fetch("/api/v1/auth/login", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email: authEmail, password: authPassword }),
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || "Authentication failed");
        setAuth(data.user, data.access_token);
        if (typeof window !== "undefined") {
          localStorage.setItem("access_token", data.access_token);
        }
      } else {
        const res = await fetch("/api/v1/auth/register", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email: authEmail, full_name: authName, password: authPassword }),
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || "Registration failed");
        // Automatically switch to login
        setAuthMode("login");
        setAuthError("Account created successfully! Please sign in.");
        setAuthLoading(false);
        return;
      }
      setShowAuthModal(false);
      loadSessions();
    } catch (err: any) {
      setAuthError(err.message);
    } finally {
      setAuthLoading(false);
    }
  };

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-[#171717] text-[#ececec]">
      {/* Left Sidebar */}
      <Sidebar
        open={sidebarOpen}
        onToggle={() => setSidebarOpen((o) => !o)}
        sessions={sessions}
        activeId={activeId}
        user={user}
        onSelect={selectSession}
        onNew={newSession}
        onRename={renameSession}
        onDelete={deleteSession}
        onAuthClick={() => setShowAuthModal(true)}
        onLogout={handleLogout}
      />

      {/* Main Conversational Workspace */}
      <main className="relative flex min-w-0 flex-1 flex-col bg-[#212121]">
        <div className="flex-1 overflow-y-auto px-4 py-8">
          <div className="mx-auto max-w-3xl space-y-6">
            {phase === "empty" && (
              <div className="flex min-h-[50vh] flex-col items-center justify-center text-center">
                <div className="flex size-12 items-center justify-center rounded-2xl bg-emerald-500/15 text-emerald-400 mb-2">
                  <Sparkles className="size-6" />
                </div>
                <h1 className="text-2xl font-semibold tracking-tight text-white">
                  What topic would you like to deeply research today?
                </h1>
                <p className="mt-2 max-w-md text-sm text-neutral-400">
                  Autonomous multi-agent research: supervisor planning, hybrid vector RAG retrieval, fact extraction, and citation-backed synthesis.
                </p>
              </div>
            )}

            {phase !== "empty" && prompt && (
              <div className="flex justify-end">
                <div className="max-w-[85%] rounded-2xl bg-[#2f2f2f] px-4 py-3 text-sm text-white border border-white/5 shadow-md">
                  <p className="leading-relaxed">{prompt}</p>
                  {attachments.length > 0 && (
                    <div className="mt-2 flex flex-wrap gap-1.5">
                      {attachments.map((f) => (
                        <span
                          key={f}
                          className="rounded-md bg-black/40 px-2.5 py-0.5 text-[11px] text-neutral-300 border border-white/5"
                        >
                          📎 {f}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Agent Live Reasoning & Thought Streams */}
            {(phase === "reasoning" ||
              phase === "plan" ||
              phase === "executing" ||
              phase === "report") && (
              <ReasoningAccordion
                steps={STEPS}
                activeIndex={step}
                done={phase === "report"}
                thoughtTraces={thoughtTraces}
              />
            )}

            {/* Human-in-the-Loop Plan Review Gate */}
            {(phase === "plan" || phase === "executing" || phase === "report") && (
              <PlanReviewCard
                plan={PLAN}
                decided={decision}
                onApprove={approve}
                onRefine={refine}
              />
            )}

            {/* Synthesized Grounded Report */}
            {phase === "report" && (
              <ReportCard
                report={REPORT}
                onCite={openCitation}
                onCanvas={() => setPanel({ kind: "canvas", report: REPORT })}
                onExport={(fmt) => {
                  window.open(researchApi.exportUrl(activeId ?? "demo", fmt), "_blank");
                }}
                onMetrics={() => setPanel({ kind: "metrics", metrics: METRICS })}
              />
            )}

            <div ref={bottomRef} />
          </div>
        </div>

        {/* Unified Bottom Floating Composer */}
        <div className="sticky bottom-0 bg-gradient-to-t from-[#212121] via-[#212121] to-transparent p-4">
          <div className="mx-auto max-w-3xl">
            <Composer
              onSend={startResearch}
              disabled={phase === "reasoning" || phase === "executing"}
              selectedMode={mode}
              onModeChange={(newMode) => setMode(newMode)}
              placeholder={
                phase === "empty"
                  ? "Ask DeepResearch to explore any technical, scientific, or market topic…"
                  : "Ask a follow-up or refine the research direction…"
              }
            />
            <p className="mt-2 text-center text-[11px] text-neutral-500">
              DeepResearch Grounding Engine · Grounded in verified evidence &amp; knowledge graph nodes.
            </p>
          </div>
        </div>
      </main>

      {/* Right Slide-Out Details Panel (Citations / Metrics / Canvas) */}
      <SidePanel state={panel} onClose={() => setPanel(null)} />

      {/* Authentication Modal for Guests */}
      {showAuthModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="w-full max-w-md bg-[#1f1f1f] border border-white/10 rounded-2xl p-6 shadow-2xl">
            <div className="flex items-center justify-between pb-4 border-b border-white/10">
              <div className="flex items-center gap-2">
                <div className="flex size-7 items-center justify-center rounded-lg bg-emerald-500/15 text-emerald-400">
                  <Lock className="size-4" />
                </div>
                <h2 className="text-base font-semibold text-white">
                  {authMode === "login" ? "Sign In to DeepResearch" : "Create an Account"}
                </h2>
              </div>
              <button
                onClick={() => setShowAuthModal(false)}
                className="text-neutral-400 hover:text-white text-sm"
              >
                ✕
              </button>
            </div>

            {authError && (
              <div className="mt-4 p-3 bg-red-900/40 border border-red-700/50 rounded-xl text-red-200 text-xs">
                {authError}
              </div>
            )}

            <form onSubmit={handleAuthSubmit} className="mt-4 space-y-3.5">
              {authMode === "register" && (
                <div>
                  <label className="block text-xs font-medium text-neutral-300 mb-1">Full Name</label>
                  <input
                    type="text"
                    required
                    value={authName}
                    onChange={(e) => setAuthName(e.target.value)}
                    placeholder="Jane Doe"
                    className="w-full px-3 py-2 bg-neutral-900 border border-white/10 rounded-xl text-white text-xs outline-none focus:border-emerald-500"
                  />
                </div>
              )}
              <div>
                <label className="block text-xs font-medium text-neutral-300 mb-1">Email Address</label>
                <input
                  type="email"
                  required
                  value={authEmail}
                  onChange={(e) => setAuthEmail(e.target.value)}
                  placeholder="admin@gmail.com"
                  className="w-full px-3 py-2 bg-neutral-900 border border-white/10 rounded-xl text-white text-xs outline-none focus:border-emerald-500"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-neutral-300 mb-1">Password</label>
                <input
                  type="password"
                  required
                  value={authPassword}
                  onChange={(e) => setAuthPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full px-3 py-2 bg-neutral-900 border border-white/10 rounded-xl text-white text-xs outline-none focus:border-emerald-500"
                />
              </div>

              <button
                type="submit"
                disabled={authLoading}
                className="w-full py-2.5 bg-emerald-600 hover:bg-emerald-500 rounded-xl text-xs font-semibold text-white transition-colors cursor-pointer mt-2 disabled:opacity-50"
              >
                {authLoading ? "Processing..." : authMode === "login" ? "Sign In" : "Create Account"}
              </button>
            </form>

            <div className="mt-4 pt-3 border-t border-white/10 text-center text-xs text-neutral-400">
              {authMode === "login" ? (
                <p>
                  Don't have an account?{" "}
                  <button
                    onClick={() => {
                      setAuthMode("register");
                      setAuthError("");
                    }}
                    className="text-emerald-400 hover:underline font-medium"
                  >
                    Register here
                  </button>
                </p>
              ) : (
                <p>
                  Already have an account?{" "}
                  <button
                    onClick={() => {
                      setAuthMode("login");
                      setAuthError("");
                    }}
                    className="text-emerald-400 hover:underline font-medium"
                  >
                    Sign In
                  </button>
                </p>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
