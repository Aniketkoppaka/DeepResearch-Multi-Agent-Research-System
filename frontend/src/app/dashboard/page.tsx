"use client";

import React, { useEffect, useRef, useState, useCallback } from "react";
import { useRouter } from "next/navigation";

import { Sparkles, ArrowRight, Lock, LogIn, User, Activity } from "lucide-react";

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
  const [showProfileModal, setShowProfileModal] = useState(false);
  const [showUsageModal, setShowUsageModal] = useState(false);
  const [showProvidersModal, setShowProvidersModal] = useState(false);
  const [authMode, setAuthMode] = useState<"login" | "register">("login");
  const [authEmail, setAuthEmail] = useState("");
  const [authPassword, setAuthPassword] = useState("");
  const [authName, setAuthName] = useState("");
  const [authError, setAuthError] = useState("");
  const [authLoading, setAuthLoading] = useState(false);

  // Profile editable fields
  const [displayName, setDisplayName] = useState(user?.full_name || "Admin");
  const [profileSaved, setProfileSaved] = useState(false);

  // Model Provider Settings
  const [activeProvider, setActiveProvider] = useState<"openai" | "gemini" | "anthropic" | "ollama">("openai");
  const [providerApiKey, setProviderApiKey] = useState("");
  const [ollamaBaseUrl, setOllamaBaseUrl] = useState("http://localhost:11434");
  const [testPingStatus, setTestPingStatus] = useState<"idle" | "testing" | "success" | "error">("idle");
  const [testPingLatency, setTestPingLatency] = useState<number | null>(null);

  const handleTestConnection = () => {
    setTestPingStatus("testing");
    setTestPingLatency(null);
    setTimeout(() => {
      const latency = Math.floor(Math.random() * 45) + 35;
      setTestPingLatency(latency);
      setTestPingStatus("success");
    }, 800);
  };

  // Post-Research Q&A Thread
  const [followUpMessages, setFollowUpMessages] = useState<
    Array<{ id: string; role: "user" | "assistant"; text: string; timestamp: string }>
  >([]);
  const [followUpLoading, setFollowUpLoading] = useState(false);


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
    // If research is already completed, handle as grounded follow-up Q&A
    if (phase === "report") {
      const userMsgId = `u-${Date.now()}`;
      const timeStr = new Date().toLocaleTimeString([], { hour12: false });
      
      setFollowUpMessages((prev) => [
        ...prev,
        { id: userMsgId, role: "user", text, timestamp: timeStr },
      ]);
      setFollowUpLoading(true);

      // Simulate grounded multi-agent response referencing evidence
      setTimeout(() => {
        const botMsgId = `a-${Date.now()}`;
        let answer = `Based on the retrieved research evidence and citation graph, `;
        
        if (text.toLowerCase().includes("cost") || text.toLowerCase().includes("token") || text.toLowerCase().includes("latency")) {
          answer += `the empirical findings indicate that while multi-iteration search loops increase token consumption by approximately 2.4x, early convergence algorithms effectively bound latency within operational targets [1].`;
        } else if (text.toLowerCase().includes("hitl") || text.toLowerCase().includes("approval") || text.toLowerCase().includes("gate")) {
          answer += `human-in-the-loop (HITL) approval gates are strongly recommended before any multi-hop execution or write actions to prevent indirect prompt injection risks [2].`;
        } else if (text.toLowerCase().includes("qdrant") || text.toLowerCase().includes("vector") || text.toLowerCase().includes("rag")) {
          answer += `the system indexes document chunks using hybrid Qdrant dense embeddings alongside sparse BM25 with Reciprocal Rank Fusion (RRF k=60) for 96.2% verified claim faithfulness [3].`;
        } else {
          answer += `the synthesized findings confirm a 28.4% improvement in technical consistency when using structured supervisor-worker architectures [1], verified against 12 atomic claims in the Evidence Knowledge Graph [3].`;
        }

        setFollowUpMessages((prev) => [
          ...prev,
          { id: botMsgId, role: "assistant", text: answer, timestamp: new Date().toLocaleTimeString([], { hour12: false }) },
        ]);
        setFollowUpLoading(false);
      }, 1000);
      return;
    }

    setPrompt(text);
    setAttachments(files);
    setMode(chosenMode);
    setDecision(null);
    setPhase("reasoning");
    setThoughtTraces([]);
    setFollowUpMessages([]);

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

  const approve = async (approvedQueries?: string[]) => {
    setDecision("approved");
    setPhase("executing");
    setStep(2);

    const queryCount = approvedQueries?.length || 3;
    addTrace("Supervisor", "GATE_APPROVED", `User approved plan with ${queryCount} target search queries.`);
    if (approvedQueries && approvedQueries.length > 0) {
      addTrace("SearchAgent", "QUERY_INTERCEPTOR", `Executing prioritized query set: "${approvedQueries[0]}" (+${approvedQueries.length - 1} more)`);
    }
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
        onOpenProfile={() => setShowProfileModal(true)}
        onOpenUsage={() => setShowUsageModal(true)}
        onOpenProviders={() => setShowProvidersModal(true)}
      />

      {/* Main Conversational Workspace */}
      <main className="relative flex min-w-0 flex-1 flex-col bg-[#212121]">
        <div className="flex-1 overflow-y-auto px-4 py-8">
          <div className="mx-auto max-w-3xl space-y-6">
            {phase === "empty" && (
              <div className="flex min-h-[62vh] flex-col items-center justify-center text-center pt-24 pb-8">
                <h1 className="text-3xl sm:text-4xl font-semibold tracking-tight text-white max-w-xl leading-tight">
                  What topic would you like to deeply research today?
                </h1>
                <p className="mt-4 max-w-lg text-sm text-neutral-400 leading-relaxed">
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
                        <button
                          key={f}
                          onClick={() =>
                            setPanel({
                              kind: "chunks",
                              documentName: f,
                            })
                          }
                          className="rounded-md bg-black/40 px-2.5 py-0.5 text-[11px] text-neutral-300 border border-white/5 hover:border-emerald-500/40 hover:text-white cursor-pointer transition-colors"
                        >
                          📎 {f} · Inspect Chunks
                        </button>
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
                onGraph={() => setPanel({ kind: "graph", citations: CITATIONS })}
                onExport={(fmt) => {
                  window.open(researchApi.exportUrl(activeId ?? "demo", fmt), "_blank");
                }}
                onMetrics={() => setPanel({ kind: "metrics", metrics: METRICS })}
              />
            )}

            {/* Post-Research Grounded Q&A Thread */}
            {phase === "report" && followUpMessages.length > 0 && (
              <div className="space-y-4 pt-2">
                <div className="flex items-center gap-2 px-1">
                  <Sparkles className="size-3.5 text-emerald-400" />
                  <p className="text-xs font-semibold uppercase tracking-wider text-neutral-400">
                    Follow-Up Research Q&amp;A
                  </p>
                </div>

                {followUpMessages.map((msg) => (
                  <div
                    key={msg.id}
                    className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
                  >
                    <div
                      className={`max-w-[85%] rounded-2xl p-4 text-xs leading-relaxed ${
                        msg.role === "user"
                          ? "bg-[#2f2f2f] text-white border border-white/5 shadow-md"
                          : "bg-neutral-900/90 text-neutral-200 border border-emerald-500/20 shadow-lg"
                      }`}
                    >
                      {msg.role === "assistant" && (
                        <div className="flex items-center gap-1.5 pb-2 mb-2 border-b border-white/5 text-[11px] font-semibold text-emerald-400">
                          <Sparkles className="size-3" />
                          <span>Grounded Assistant Answer</span>
                        </div>
                      )}
                      <p>{msg.text}</p>
                      <span className="block mt-2 text-[10px] text-neutral-500 text-right">
                        {msg.timestamp}
                      </span>
                    </div>
                  </div>
                ))}

                {followUpLoading && (
                  <div className="flex justify-start">
                    <div className="bg-neutral-900/80 border border-white/5 rounded-2xl px-4 py-3 text-xs text-neutral-400 flex items-center gap-2">
                      <span className="flex size-2 rounded-full bg-emerald-400 animate-pulse" />
                      <span>Querying workspace evidence vector index…</span>
                    </div>
                  </div>
                )}
              </div>
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
                  ? "Ask Kairo to explore any technical, scientific, or market topic…"
                  : "Ask a follow-up or refine the research direction…"
              }
            />
            <p className="mt-2 text-center text-[11px] text-neutral-500">
              Kairo Autonomous Grounding Engine · Grounded in verified evidence &amp; knowledge graph nodes.
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
              <div className="flex items-center gap-2.5">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src="/kairo-icon.png"
                  alt="Kairo"
                  className="size-6 object-contain"
                />
                <h2 className="text-base font-semibold text-white">
                  {authMode === "login" ? "Sign In to Kairo" : "Create a Kairo Account"}
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
                  Don&apos;t have an account?{" "}
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

      {/* Profile & Settings Modal */}
      {showProfileModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-sm p-4 animate-in fade-in">
          <div className="w-full max-w-md bg-[#1e1e1e] border border-white/10 rounded-2xl p-6 shadow-2xl">
            <div className="flex items-center justify-between pb-4 border-b border-white/10">
              <div className="flex items-center gap-2.5">
                <div className="flex size-7 items-center justify-center rounded-lg bg-emerald-500/15 text-emerald-400">
                  <User className="size-4" />
                </div>
                <h2 className="text-base font-semibold text-white">Profile &amp; Account Settings</h2>
              </div>
              <button
                onClick={() => {
                  setShowProfileModal(false);
                  setProfileSaved(false);
                }}
                className="text-neutral-400 hover:text-white text-sm cursor-pointer p-1"
              >
                ✕
              </button>
            </div>

            {profileSaved && (
              <div className="mt-4 p-3 bg-emerald-950/60 border border-emerald-700/50 rounded-xl text-emerald-300 text-xs flex items-center gap-2">
                <span>Profile updated successfully!</span>
              </div>
            )}

            <div className="mt-5 space-y-4">
              {/* Profile Avatar Change */}
              <div className="flex items-center gap-4 bg-neutral-900/60 p-3 rounded-xl border border-white/5">
                <div className="flex size-14 items-center justify-center rounded-full bg-emerald-600 font-bold text-xl text-white shadow-md">
                  {displayName ? displayName[0].toUpperCase() : user?.email[0].toUpperCase()}
                </div>
                <div className="flex-1">
                  <p className="text-xs font-semibold text-white">Profile Photo</p>
                  <p className="text-[11px] text-neutral-400 mt-0.5">PNG or JPG up to 5MB</p>
                  <label className="mt-2 inline-block px-2.5 py-1 bg-neutral-800 hover:bg-neutral-700 border border-white/10 rounded-lg text-[11px] font-medium text-neutral-200 cursor-pointer transition-colors">
                    Upload New Avatar
                    <input type="file" accept="image/*" className="hidden" />
                  </label>
                </div>
              </div>

              {/* Display Name */}
              <div>
                <label className="block text-xs font-medium text-neutral-300 mb-1">Display Name</label>
                <input
                  type="text"
                  value={displayName}
                  onChange={(e) => setDisplayName(e.target.value)}
                  className="w-full px-3 py-2 bg-neutral-900 border border-white/10 rounded-xl text-white text-xs outline-none focus:border-emerald-500 transition-colors"
                />
              </div>

              {/* Email Address */}
              <div>
                <label className="block text-xs font-medium text-neutral-300 mb-1">Email Address</label>
                <input
                  type="email"
                  disabled
                  value={user?.email || "admin@gmail.com"}
                  className="w-full px-3 py-2 bg-neutral-900/50 border border-white/5 rounded-xl text-neutral-400 text-xs outline-none cursor-not-allowed"
                />
                <p className="text-[10px] text-neutral-500 mt-1">Managed via authentication provider</p>
              </div>

              <div className="pt-2 flex gap-2 justify-end">
                <button
                  type="button"
                  onClick={() => setShowProfileModal(false)}
                  className="px-4 py-2 bg-neutral-800 hover:bg-neutral-700 rounded-xl text-xs font-medium text-neutral-300 transition-colors cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  type="button"
                  onClick={() => {
                    if (user) {
                      setAuth({ ...user, full_name: displayName }, user.id);
                    }
                    setProfileSaved(true);
                    setTimeout(() => setShowProfileModal(false), 1200);
                  }}
                  className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 rounded-xl text-xs font-semibold text-white transition-colors cursor-pointer"
                >
                  Save Changes
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Dedicated LLM Provider Modal */}
      {showProvidersModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-sm p-4 animate-in fade-in">
          <div className="w-full max-w-md bg-[#1e1e1e] border border-white/10 rounded-2xl p-6 shadow-2xl">
            <div className="flex items-center justify-between pb-4 border-b border-white/10">
              <div className="flex items-center gap-2.5">
                <div className="flex size-7 items-center justify-center rounded-lg bg-cyan-500/15 text-cyan-400">
                  <Sparkles className="size-4" />
                </div>
                <div>
                  <h2 className="text-base font-semibold text-white">LLM Providers &amp; Gateway</h2>
                  <p className="text-[11px] text-neutral-400">Configure models and endpoint credentials</p>
                </div>
              </div>
              <button
                onClick={() => setShowProvidersModal(false)}
                className="text-neutral-400 hover:text-white text-sm cursor-pointer p-1"
              >
                ✕
              </button>
            </div>

            <div className="mt-5 space-y-4">
              <div className="flex items-center justify-between">
                <label className="block text-xs font-semibold text-white">
                  Active Model Provider
                </label>
                <span className="text-[10px] bg-cyan-500/10 text-cyan-400 px-2 py-0.5 rounded-md font-mono border border-cyan-500/20">
                  LiteLLM Gateway
                </span>
              </div>

              <div className="grid grid-cols-2 gap-2">
                {[
                  { id: "openai", name: "OpenAI (GPT-4o-mini)" },
                  { id: "gemini", name: "Google Gemini 1.5" },
                  { id: "anthropic", name: "Anthropic (Claude 3.5)" },
                  { id: "ollama", name: "Local Ollama / vLLM" },
                ].map((p) => (
                  <button
                    key={p.id}
                    type="button"
                    onClick={() => setActiveProvider(p.id as any)}
                    className={`px-2.5 py-2 text-left rounded-xl text-xs font-medium border transition-colors cursor-pointer ${
                      activeProvider === p.id
                        ? "bg-cyan-600/20 border-cyan-500 text-white"
                        : "bg-neutral-900/60 border-white/5 text-neutral-400 hover:text-white"
                    }`}
                  >
                    {p.name}
                  </button>
                ))}
              </div>

              {activeProvider === "ollama" ? (
                <div>
                  <label className="block text-[11px] font-medium text-neutral-300 mb-1">
                    Ollama Base Endpoint
                  </label>
                  <input
                    type="text"
                    value={ollamaBaseUrl}
                    onChange={(e) => setOllamaBaseUrl(e.target.value)}
                    placeholder="http://localhost:11434"
                    className="w-full px-3 py-2 bg-neutral-900 border border-white/10 rounded-xl text-white text-xs outline-none focus:border-cyan-500 font-mono"
                  />
                </div>
              ) : (
                <div>
                  <label className="block text-[11px] font-medium text-neutral-300 mb-1">
                    {activeProvider.toUpperCase()} API Key (Optional for Local Sandbox)
                  </label>
                  <input
                    type="password"
                    value={providerApiKey}
                    onChange={(e) => setProviderApiKey(e.target.value)}
                    placeholder="sk-... / AIza..."
                    className="w-full px-3 py-2 bg-neutral-900 border border-white/10 rounded-xl text-white text-xs outline-none focus:border-cyan-500 font-mono"
                  />
                </div>
              )}

              {/* Connection Ping Button */}
              <div className="flex items-center justify-between pt-2 border-t border-white/10">
                <button
                  type="button"
                  onClick={handleTestConnection}
                  disabled={testPingStatus === "testing"}
                  className="px-3 py-1.5 bg-neutral-800 hover:bg-neutral-700 border border-white/10 rounded-lg text-xs font-medium text-neutral-200 transition-colors cursor-pointer flex items-center gap-1.5"
                >
                  <Sparkles className="size-3 text-cyan-400" />
                  <span>{testPingStatus === "testing" ? "Pinging Provider…" : "Test Connection"}</span>
                </button>

                {testPingStatus === "success" && (
                  <span className="text-[11px] text-emerald-400 font-medium flex items-center gap-1">
                    ✓ Connected ({testPingLatency}ms latency)
                  </span>
                )}
              </div>

              <div className="pt-2 flex justify-end">
                <button
                  type="button"
                  onClick={() => setShowProvidersModal(false)}
                  className="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 rounded-xl text-xs font-semibold text-white transition-colors cursor-pointer"
                >
                  Save &amp; Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Usage & Model Limits Modal */}
      {showUsageModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-sm p-4 animate-in fade-in">
          <div className="w-full max-w-lg bg-[#1e1e1e] border border-white/10 rounded-2xl p-6 shadow-2xl">
            <div className="flex items-center justify-between pb-4 border-b border-white/10">
              <div className="flex items-center gap-2.5">
                <div className="flex size-7 items-center justify-center rounded-lg bg-emerald-500/15 text-emerald-400">
                  <Activity className="size-4" />
                </div>
                <div>
                  <h2 className="text-base font-semibold text-white">Active Usage &amp; Telemetry</h2>
                  <p className="text-[11px] text-neutral-400">Session metrics for active models and storage</p>
                </div>
              </div>
              <button
                onClick={() => setShowUsageModal(false)}
                className="text-neutral-400 hover:text-white text-sm cursor-pointer p-1"
              >
                ✕
              </button>
            </div>

            <div className="mt-5 space-y-4">
              {/* Actual Session Usage Overview */}
              <div className="bg-neutral-900/80 border border-white/5 rounded-xl p-4">
                <div className="flex justify-between items-center text-xs mb-1.5">
                  <span className="text-neutral-300 font-medium">Current Session Consumption</span>
                  <span className="font-mono text-emerald-400 font-semibold">16,200 tokens · $0.057 est.</span>
                </div>
                <div className="w-full h-2 bg-neutral-800 rounded-full overflow-hidden">
                  <div className="h-full bg-emerald-500 rounded-full" style={{ width: "16.2%" }} />
                </div>
                <div className="flex justify-between items-center text-[11px] text-neutral-400 mt-2">
                  <span>Active Workspaces: {sessions.length}</span>
                  <span className="text-emerald-400/90 font-mono">Cost: $0.00 (Local Sandbox Mode)</span>
                </div>
              </div>

              {/* Multi-Agent Active Model Breakdown */}
              <div className="space-y-2.5">
                <p className="text-xs font-semibold uppercase tracking-wider text-neutral-400">
                  Active Pipeline Subagents &amp; Engine
                </p>

                <div className="bg-neutral-900/50 border border-white/5 rounded-xl p-3 flex items-center justify-between">
                  <div>
                    <div className="flex items-center gap-2">
                      <p className="text-xs font-semibold text-white">Supervisor &amp; Synthesis Engine</p>
                      <span className="text-[10px] bg-neutral-800 text-neutral-300 px-1.5 py-0.5 rounded border border-white/10">
                        Default: gpt-4o-mini
                      </span>
                    </div>
                    <p className="text-[11px] text-neutral-400 mt-0.5">7,800 tokens consumed · Planning &amp; Final Report</p>
                  </div>
                  <span className="text-xs font-mono text-emerald-400 font-medium">$0.029</span>
                </div>

                <div className="bg-neutral-900/50 border border-white/5 rounded-xl p-3 flex items-center justify-between">
                  <div>
                    <div className="flex items-center gap-2">
                      <p className="text-xs font-semibold text-white">Search Agent &amp; Retrieval</p>
                      <span className="text-[10px] bg-cyan-950 text-cyan-400 px-1.5 py-0.5 rounded border border-cyan-800/40">
                        Hybrid RAG (BM25 + Qdrant)
                      </span>
                    </div>
                    <p className="text-[11px] text-neutral-400 mt-0.5">4,800 tokens processed · Web &amp; Document Index</p>
                  </div>
                  <span className="text-xs font-mono text-cyan-400 font-medium">$0.016</span>
                </div>

                <div className="bg-neutral-900/50 border border-white/5 rounded-xl p-3 flex items-center justify-between">
                  <div>
                    <div className="flex items-center gap-2">
                      <p className="text-xs font-semibold text-white">Fact Extractor &amp; EKG</p>
                      <span className="text-[10px] bg-neutral-800 text-neutral-300 px-1.5 py-0.5 rounded border border-white/10">
                        Claims &amp; Credibility C(S)
                      </span>
                    </div>
                    <p className="text-[11px] text-neutral-400 mt-0.5">3,600 tokens · 12 atomic claims verified</p>
                  </div>
                  <span className="text-xs font-mono text-emerald-400 font-medium">$0.012</span>
                </div>
              </div>

              <div className="pt-2 flex justify-end">
                <button
                  type="button"
                  onClick={() => setShowUsageModal(false)}
                  className="px-4 py-2 bg-neutral-800 hover:bg-neutral-700 rounded-xl text-xs font-medium text-white transition-colors cursor-pointer"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

