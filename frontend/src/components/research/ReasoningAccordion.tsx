import React, { useState } from "react";
import {

  ChevronDown,
  Loader2,
  Check,
  Compass,
  Database,
  Binary,
  FileCheck,
  Terminal,
  Cpu,
} from "lucide-react";
import type { Step, ThoughtTrace } from "@/lib/research-data";

type Props = {
  steps: Step[];
  activeIndex: number;
  done: boolean;
  thoughtTraces: ThoughtTrace[];
};

export function ReasoningAccordion({
  steps,
  activeIndex,
  done,
  thoughtTraces,
}: Props) {
  const [open, setOpen] = useState(true);

  const getStepIcon = (iconName: string) => {
    switch (iconName) {
      case "Compass":
        return <Compass className="size-4 text-emerald-400" />;
      case "Database":
        return <Database className="size-4 text-blue-400" />;
      case "Binary":
        return <Binary className="size-4 text-purple-400" />;
      case "FileCheck":
        return <FileCheck className="size-4 text-emerald-400" />;
      default:
        return <Cpu className="size-4 text-emerald-400" />;
    }
  };

  return (
    <div className="surface-panel overflow-hidden bg-[#212121] border border-white/10 rounded-2xl shadow-lg">
      <button
        onClick={() => setOpen((o) => !o)}
        className="flex w-full items-center gap-2.5 px-4 py-3 text-left cursor-pointer hover:bg-white/5 transition-colors"
      >
        {done ? (
          <Check className="size-4 text-emerald-400" />
        ) : (
          <Loader2 className="size-4 animate-spin text-emerald-400" />
        )}
        <span className="text-sm font-semibold text-white">
          {done ? "Autonomous multi-agent execution completed" : "Multi-Agent Thinking & Execution Process…"}
        </span>
        {!done && (
          <span className="flex gap-1">
            {[0, 1, 2].map((i) => (
              <span
                key={i}
                className="size-1.5 animate-pulse rounded-full bg-emerald-400"
                style={{ animationDelay: `${i * 0.18}s` }}
              />
            ))}
          </span>
        )}
        <span className="flex-1" />
        <ChevronDown
          className={`size-4 text-neutral-400 transition-transform ${open ? "rotate-180" : ""}`}
        />
      </button>

      {open && (
        <div className="border-t border-white/10 px-4 py-3 space-y-4">
          {/* High-level agent milestones */}
          <ol className="space-y-3">
            {steps.map((s, i) => {
              const state = i < activeIndex || done ? "done" : i === activeIndex ? "active" : "idle";
              return (
                <li
                  key={s.label}
                  className={`flex gap-3 text-sm transition-opacity ${state === "idle" ? "opacity-35" : ""}`}
                >
                  <span className="mt-0.5 shrink-0">{getStepIcon(s.iconName)}</span>
                  <div className="min-w-0 flex-1">
                    <p
                      className={`font-medium ${
                        state === "active" ? "text-white font-semibold" : "text-neutral-300"
                      }`}
                    >
                      Step {i + 1}: {s.label}
                      {state === "active" && "…"}
                    </p>
                    {state !== "idle" && (
                      <p className="mt-0.5 text-xs leading-relaxed text-neutral-400">
                        {s.detail}
                      </p>
                    )}
                  </div>
                  {state === "done" && <Check className="ml-auto mt-0.5 size-4 shrink-0 text-emerald-400" />}
                  {state === "active" && <Loader2 className="ml-auto mt-0.5 size-4 shrink-0 animate-spin text-emerald-400" />}
                </li>
              );
            })}
          </ol>

          {/* Antigravity-style detailed Agent Thought Stream / Trace Terminal */}
          {thoughtTraces.length > 0 && (
            <div className="rounded-xl border border-white/10 bg-black/40 p-3 font-mono text-[11px] text-neutral-300">
              <div className="flex items-center gap-2 border-b border-white/10 pb-2 mb-2 text-neutral-400">
                <Terminal className="size-3.5 text-emerald-400" />
                <span className="font-semibold text-white">Live Agent Thought &amp; Tool Traces</span>
              </div>
              <div className="space-y-1.5 max-h-48 overflow-y-auto pr-1">
                {thoughtTraces.map((trace, idx) => (
                  <div key={idx} className="flex items-start gap-2">
                    <span className="text-neutral-500 shrink-0">[{trace.timestamp}]</span>
                    <span className="text-emerald-400 font-semibold shrink-0">@{trace.agent}:</span>
                    <span className="text-white shrink-0">{trace.action}</span>
                    <span className="text-neutral-400 truncate flex-1">— {trace.detail}</span>
                    {trace.status === "running" ? (
                      <span className="text-cyan-400 animate-pulse">[RUNNING]</span>
                    ) : (
                      <span className="text-emerald-500">[OK]</span>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
