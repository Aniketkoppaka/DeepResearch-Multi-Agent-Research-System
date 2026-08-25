"use client";

import { useEffect, useRef, useState } from "react";
import { Telescope } from "lucide-react";
import { Sidebar } from "@/components/research/Sidebar";
import { Composer } from "@/components/research/Composer";
import { ReasoningAccordion } from "@/components/research/ReasoningAccordion";
import { PlanReviewCard } from "@/components/research/PlanReviewCard";
import { ReportCard } from "@/components/research/ReportCard";
import { SidePanel, type PanelState } from "@/components/research/SidePanel";
import { researchApi } from "@/lib/research-api";
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
} from "@/lib/research-data";

type Phase = "empty" | "reasoning" | "plan" | "executing" | "report";

export default function DashboardPage() {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [sessions, setSessions] = useState<Session[]>(SESSIONS);
  const [activeId, setActiveId] = useState<string | null>(null);
  const [mode, setMode] = useState<ResearchMode>("deep");
  const [phase, setPhase] = useState<Phase>("empty");
  const [prompt, setPrompt] = useState("");
  const [attachments, setAttachments] = useState<string[]>([]);
  const [step, setStep] = useState(0);
  const [decision, setDecision] = useState<"approved" | "refine" | null>(null);
  const [panel, setPanel] = useState<PanelState>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [phase, step, decision]);

  const runSteps = (from: number, to: number, then: () => void) => {
    let i = from;
    setStep(i);
    const tick = setInterval(() => {
      i += 1;
      setStep(i);
      if (i >= to) {
        clearInterval(tick);
        then();
      }
    }, 1100);
  };

  const startResearch = async (text: string, files: string[]) => {
    setPrompt(text);
    setAttachments(files);
    setDecision(null);
    setPhase("reasoning");
    const ws = activeId
      ? sessions.find((s) => s.id === activeId)!
      : await researchApi.createWorkspace(text.slice(0, 48), mode);
    if (!activeId) {
      setSessions((p) => [ws, ...p]);
      setActiveId(ws.id);
    }
    void researchApi.generatePlan(ws.id, text);
    runSteps(0, 2, () => setPhase("plan"));
  };

  const approve = async () => {
    setDecision("approved");
    setPhase("executing");
    if (activeId) {
      void researchApi.reviewPlan(activeId, true);
      void researchApi.execute(activeId);
    }
    runSteps(2, 4, () => setPhase("report"));
  };

  const refine = async (feedback: string) => {
    setDecision("refine");
    setPhase("reasoning");
    if (activeId) void researchApi.reviewPlan(activeId, false, feedback);
    runSteps(0, 2, () => {
      setDecision(null);
      setPhase("plan");
    });
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
  };

  const newSession = () => {
    setActiveId(null);
    setPhase("empty");
    setPrompt("");
    setAttachments([]);
    setDecision(null);
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

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-[#171717] text-[#ececec]">
      <Sidebar
        open={sidebarOpen}
        onToggle={() => setSidebarOpen((o) => !o)}
        sessions={sessions}
        activeId={activeId}
        onSelect={selectSession}
        onNew={newSession}
        onRename={renameSession}
        onDelete={deleteSession}
      />

      <main className="relative flex min-w-0 flex-1 flex-col bg-[#212121]">
        <div className="flex-1 overflow-y-auto px-4 py-8">
          <div className="mx-auto max-w-3xl space-y-6">
            {phase === "empty" && (
              <div className="flex min-h-[50vh] flex-col items-center justify-center text-center">
                <div className="flex size-12 items-center justify-center rounded-2xl bg-emerald-500/15 text-emerald-400">
                  <Telescope className="size-6" />
                </div>
                <h1 className="mt-4 text-2xl font-semibold tracking-tight text-white">
                  What topic would you like to deeply research today?
                </h1>
                <p className="mt-2 max-w-md text-sm text-neutral-400">
                  Multi-agent research planner, autonomous dual-vector RAG search, fact extraction, and citation-backed synthesis.
                </p>

                <div className="mt-6 flex flex-wrap justify-center gap-2">
                  {MODES.map((m) => {
                    const sel = m.id === mode;
                    return (
                      <button
                        key={m.id}
                        onClick={() => setMode(m.id)}
                        className={`flex items-center gap-2 rounded-full border px-3.5 py-1.5 text-xs font-medium transition-colors ${
                          sel
                            ? "border-emerald-500 bg-emerald-500/15 text-emerald-400"
                            : "border-white/10 text-neutral-400 hover:bg-neutral-800 hover:text-white"
                        }`}
                      >
                        <span>{m.emoji}</span>
                        <span>{m.label}</span>
                        <span className="text-[11px] opacity-60">· {m.hint}</span>
                      </button>
                    );
                  })}
                </div>
              </div>
            )}

            {phase !== "empty" && prompt && (
              <div className="flex justify-end">
                <div className="max-w-[85%] rounded-3xl bg-[#2f2f2f] px-4 py-3 text-sm text-white">
                  <p className="leading-relaxed">{prompt}</p>
                  {attachments.length > 0 && (
                    <div className="mt-2 flex flex-wrap gap-1.5">
                      {attachments.map((f) => (
                        <span
                          key={f}
                          className="rounded-full bg-neutral-900 px-2.5 py-0.5 text-[11px] text-neutral-300"
                        >
                          📎 {f}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            )}

            {(phase === "reasoning" ||
              phase === "plan" ||
              phase === "executing" ||
              phase === "report") && (
              <ReasoningAccordion steps={STEPS} activeIndex={step} done={phase === "report"} />
            )}

            {(phase === "plan" || phase === "executing" || phase === "report") && (
              <PlanReviewCard
                plan={PLAN}
                decided={decision}
                onApprove={approve}
                onRefine={refine}
              />
            )}

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

        <div className="sticky bottom-0 bg-gradient-to-t from-[#212121] via-[#212121] to-transparent p-4">
          <div className="mx-auto max-w-3xl">
            <Composer
              onSend={startResearch}
              disabled={phase === "reasoning" || phase === "executing"}
              placeholder={
                phase === "empty"
                  ? `Ask DeepResearch to explore any topic…`
                  : "Ask a follow-up or refine the research direction…"
              }
            />
            <p className="mt-2 text-center text-[11px] text-neutral-500">
              DeepResearch Grounding Engine · All findings indexed to verified evidence sources.
            </p>
          </div>
        </div>
      </main>

      <SidePanel state={panel} onClose={() => setPanel(null)} />
    </div>
  );
}
