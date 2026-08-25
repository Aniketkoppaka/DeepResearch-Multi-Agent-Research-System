import { useState } from "react";
import { CheckCircle2, ClipboardList, PencilLine, Send } from "lucide-react";
import type { Plan } from "@/lib/research-data";

type Props = {
  plan: Plan;
  decided: "approved" | "refine" | null;
  onApprove: () => void;
  onRefine: (feedback: string) => void;
};

export function PlanReviewCard({ plan, decided, onApprove, onRefine }: Props) {
  const [showFeedback, setShowFeedback] = useState(false);
  const [feedback, setFeedback] = useState("");

  return (
    <div className="surface-panel glow-ring p-5 bg-[#212121] border border-white/10 rounded-2xl">
      <div className="flex items-center gap-2 pb-3">
        <ClipboardList className="size-4 text-emerald-400" />
        <h3 className="text-sm font-semibold text-white">Research Plan · Awaiting your review</h3>
      </div>

      <p className="text-sm leading-relaxed text-neutral-300">{plan.objective}</p>

      <div className="mt-4">
        <p className="text-xs font-semibold uppercase tracking-wide text-neutral-400">
          Research Questions
        </p>
        <ul className="mt-2 space-y-2">
          {plan.questions.map((q, i) => (
            <li key={q} className="flex gap-2.5 text-sm leading-relaxed text-neutral-300">
              <span className="mt-0.5 shrink-0 rounded-md bg-neutral-800 px-1.5 py-0.5 text-[11px] font-semibold text-white">
                RQ{i + 1}
              </span>
              <span>{q}</span>
            </li>
          ))}
        </ul>
      </div>

      <div className="mt-4">
        <p className="text-xs font-semibold uppercase tracking-wide text-neutral-400">
          Hypotheses
        </p>
        <ul className="mt-2 space-y-2.5">
          {plan.hypotheses.map((h, i) => (
            <li key={h.text} className="text-sm">
              <div className="flex gap-2.5 text-neutral-300">
                <span className="mt-0.5 shrink-0 rounded-md bg-neutral-800 px-1.5 py-0.5 text-[11px] font-semibold text-white">
                  H{i + 1}
                </span>
                <span className="leading-relaxed">{h.text}</span>
              </div>
              <div className="ml-9 mt-1.5 flex items-center gap-2">
                <div className="h-1.5 w-32 overflow-hidden rounded-full bg-neutral-800">
                  <div className="h-full rounded-full bg-emerald-500" style={{ width: `${h.confidence}%` }} />
                </div>
                <span className="text-xs text-neutral-400">{h.confidence}% confidence</span>
              </div>
            </li>
          ))}
        </ul>
      </div>

      <div className="mt-5 border-t border-white/10 pt-4">
        {decided === "approved" ? (
          <div className="flex items-center gap-2 text-xs font-medium text-emerald-400">
            <CheckCircle2 className="size-4" />
            <span>Plan approved — Autonomous execution in progress</span>
          </div>
        ) : (
          <div className="space-y-3">
            <div className="flex flex-wrap items-center gap-2">
              <button
                onClick={onApprove}
                className="flex items-center gap-1.5 rounded-full bg-emerald-600 px-4 py-2 text-xs font-semibold text-white transition-opacity hover:opacity-90"
              >
                <CheckCircle2 className="size-3.5" />
                <span>Approve &amp; Begin Research</span>
              </button>

              <button
                onClick={() => setShowFeedback((s) => !s)}
                className="flex items-center gap-1.5 rounded-full border border-white/10 px-3.5 py-2 text-xs font-medium text-neutral-300 transition-colors hover:bg-neutral-800 hover:text-white"
              >
                <PencilLine className="size-3.5" />
                <span>Request Changes / Refine</span>
              </button>
            </div>

            {showFeedback && (
              <div className="flex gap-2 pt-1">
                <input
                  type="text"
                  value={feedback}
                  onChange={(e) => setFeedback(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" && feedback.trim()) {
                      onRefine(feedback.trim());
                      setFeedback("");
                      setShowFeedback(false);
                    }
                  }}
                  placeholder="What would you like adjusted in this plan?"
                  className="flex-1 rounded-xl bg-neutral-900 border border-white/10 px-3 py-2 text-xs text-white outline-none placeholder:text-neutral-500"
                />
                <button
                  onClick={() => {
                    if (!feedback.trim()) return;
                    onRefine(feedback.trim());
                    setFeedback("");
                    setShowFeedback(false);
                  }}
                  className="flex items-center gap-1 rounded-xl bg-white px-3 py-2 text-xs font-semibold text-black hover:opacity-90"
                >
                  <Send className="size-3" />
                  <span>Send</span>
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
