import React from "react";
import {
  AlertTriangle,
  BadgeCheck,
  BarChart3,
  ExternalLink,
  Layers,
  Quote,
  X,
} from "lucide-react";

import { Markdown } from "./Markdown";
import { KnowledgeGraphCanvas } from "./KnowledgeGraphCanvas";
import { DocumentChunkInspector, type DocumentChunk } from "./DocumentChunkInspector";
import type { Citation, Metrics } from "@/lib/research-data";

export type PanelState =
  | { kind: "citation"; citation: Citation }
  | { kind: "metrics"; metrics: Metrics }
  | { kind: "canvas"; report: string }
  | { kind: "graph"; citations: Citation[] }
  | { kind: "chunks"; documentName?: string; chunks?: DocumentChunk[] }
  | null;

const CLAIM_COLORS: Record<Citation["claim"], string> = {
  FACT: "bg-emerald-500/15 text-emerald-400",
  FINDING: "bg-blue-500/20 text-blue-400",
  STATISTIC: "bg-purple-500/20 text-purple-400",
  HYPOTHESIS: "bg-amber-500/20 text-amber-400",
};

export function SidePanel({ state, onClose }: { state: PanelState; onClose: () => void }) {
  const open = state !== null;

  return (
    <aside
      className={`z-20 h-full shrink-0 overflow-hidden bg-[#171717] transition-[width] duration-300 ease-out ${
        open ? "w-full border-l border-white/10 md:w-[420px]" : "w-0"
      }`}
    >
      {state && (
        <div className="flex h-full w-full flex-col md:w-[420px]">
          <div className="flex items-center gap-2 border-b border-white/10 px-4 py-3">
            {state.kind === "citation" && (
              <>
                <span className="rounded-md bg-emerald-500/15 px-2 py-0.5 text-xs font-semibold text-emerald-400">
                  [{state.citation.id}]
                </span>
                {state.citation.verified && (
                  <span className="flex items-center gap-1 text-xs text-emerald-400">
                    <BadgeCheck className="size-3.5" /> Verified source
                  </span>
                )}
              </>
            )}
            {state.kind === "metrics" && (
              <h3 className="flex items-center gap-2 text-sm font-semibold text-white">
                <BarChart3 className="size-4 text-emerald-400" /> Metrics &amp; Telemetry
              </h3>
            )}
            {state.kind === "canvas" && <h3 className="text-sm font-semibold text-white">Report Canvas</h3>}
            {state.kind === "graph" && (
              <h3 className="flex items-center gap-2 text-sm font-semibold text-white">
                <span className="flex size-2 rounded-full bg-emerald-400 animate-pulse" />
                Evidence Knowledge Graph (EKG)
              </h3>
            )}
            {state.kind === "chunks" && (
              <h3 className="flex items-center gap-2 text-sm font-semibold text-white">
                <Layers className="size-4 text-emerald-400" />
                Document Chunks &amp; Ingestion
              </h3>
            )}
            <button
              onClick={onClose}
              aria-label="Close panel"
              className="ml-auto rounded-lg p-1.5 text-neutral-400 transition-colors hover:bg-neutral-800 hover:text-white"
            >
              <X className="size-4" />
            </button>
          </div>

          <div className="flex-1 overflow-y-auto p-5 text-sm">
            {state.kind === "citation" && (
              <div className="space-y-4">
                <div>
                  <span
                    className={`inline-block rounded-md px-2 py-0.5 text-[11px] font-semibold ${
                      CLAIM_COLORS[state.citation.claim]
                    }`}
                  >
                    {state.citation.claim}
                  </span>
                  <h4 className="mt-2 text-base font-semibold leading-snug text-white">
                    {state.citation.title}
                  </h4>
                  <p className="mt-1 text-xs text-neutral-400">{state.citation.publisher}</p>
                </div>

                <div className="rounded-xl border border-white/10 bg-[#212121] p-3.5">
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-neutral-400">Source Credibility C(S)</span>
                    <span className="font-semibold text-emerald-400">
                      {Math.round(state.citation.credibility * 100)}%
                    </span>
                  </div>
                  <div className="mt-2 h-1.5 overflow-hidden rounded-full bg-neutral-800">
                    <div
                      className="h-full rounded-full bg-emerald-500"
                      style={{ width: `${state.citation.credibility * 100}%` }}
                    />
                  </div>
                  <p className="mt-2 text-[11px] text-neutral-400">
                    {state.citation.credibilityLabel}
                  </p>
                </div>

                <div>
                  <p className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide text-neutral-400">
                    <Quote className="size-3 text-emerald-400" />
                    Exact Quote Passage
                  </p>
                  <blockquote className="mt-2 rounded-xl border-l-2 border-emerald-500 bg-[#212121] p-3 text-xs italic leading-relaxed text-neutral-300">
                    &ldquo;{state.citation.quote}&rdquo;
                  </blockquote>
                </div>

                {state.citation.contradiction && (
                  <div className="rounded-xl border border-amber-500/30 bg-amber-500/10 p-3 text-xs text-amber-200">
                    <div className="flex items-center gap-1.5 font-semibold text-amber-400">
                      <AlertTriangle className="size-3.5" /> Contradiction Note
                    </div>
                    <p className="mt-1 leading-relaxed">{state.citation.contradiction}</p>
                  </div>
                )}

                <a
                  href={state.citation.url}
                  target="_blank"
                  rel="noreferrer"
                  className="flex items-center justify-center gap-1.5 rounded-xl bg-white px-4 py-2 text-xs font-semibold text-black transition-opacity hover:opacity-90"
                >
                  <span>Open Primary Source</span>
                  <ExternalLink className="size-3" />
                </a>
              </div>
            )}

            {state.kind === "metrics" && (
              <div className="space-y-4">
                <div className="grid grid-cols-3 gap-2">
                  <MetricCard
                    label="Faithfulness"
                    value={`${Math.round(state.metrics.faithfulness * 100)}%`}
                    hint="Grounded claims"
                  />
                  <MetricCard
                    label="Relevance"
                    value={`${Math.round(state.metrics.answerRelevance * 100)}%`}
                    hint="Plan alignment"
                  />
                  <MetricCard
                    label="Precision"
                    value={`${Math.round(state.metrics.contextPrecision * 100)}%`}
                    hint="Retrieved signal"
                  />
                </div>

                <div className="rounded-xl border border-white/10 bg-[#212121] p-4">
                  <h4 className="text-xs font-semibold uppercase tracking-wide text-neutral-400">
                    Subagent Telemetry Breakdown
                  </h4>
                  <ul className="mt-3 space-y-2.5">
                    {state.metrics.agents.map((a) => (
                      <li key={a.agent} className="flex items-center justify-between text-xs">
                        <span className="text-neutral-300">{a.agent}</span>
                        <div className="text-right">
                          <span className="font-mono text-neutral-400">
                            {a.tokens.toLocaleString()} tokens
                          </span>
                          <span className="ml-2 font-mono text-emerald-400">
                            ${a.cost.toFixed(3)}
                          </span>
                        </div>
                      </li>
                    ))}
                  </ul>
                  <div className="mt-3 flex justify-between border-t border-white/10 pt-2 text-xs font-semibold">
                    <span className="text-white">Total Estimated Cost</span>
                    <span className="font-mono text-emerald-400">
                      $
                      {state.metrics.agents
                        .reduce((acc, x) => acc + x.cost, 0)
                        .toFixed(3)}
                    </span>
                  </div>
                </div>
              </div>
            )}

            {state.kind === "canvas" && (
              <div className="space-y-4">
                <Markdown source={state.report} />
              </div>
            )}

            {state.kind === "graph" && (
              <div className="h-[600px] w-full">
                <KnowledgeGraphCanvas citations={state.citations} />
              </div>
            )}

            {state.kind === "chunks" && (
              <DocumentChunkInspector
                documentName={state.documentName}
                chunks={state.chunks}
              />
            )}
          </div>
        </div>
      )}
    </aside>
  );
}

function MetricCard({
  label,
  value,
  hint,
}: {
  label: string;
  value: string;
  hint: string;
}) {
  return (
    <div className="rounded-xl border border-white/10 bg-[#212121] p-3 text-center">
      <div className="font-mono text-lg font-bold text-emerald-400">{value}</div>
      <div className="mt-0.5 text-[11px] font-medium text-white">{label}</div>
      <div className="text-[10px] text-neutral-400">{hint}</div>
    </div>
  );
}
