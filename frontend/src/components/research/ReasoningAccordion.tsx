import { useState } from "react";
import { Check, ChevronDown, Loader2 } from "lucide-react";
import type { Step } from "@/lib/research-data";

type Props = { steps: Step[]; activeIndex: number; done: boolean };

export function ReasoningAccordion({ steps, activeIndex, done }: Props) {
  const [open, setOpen] = useState(true);

  return (
    <div className="surface-panel overflow-hidden bg-[#212121] border border-white/10 rounded-2xl">
      <button
        onClick={() => setOpen((o) => !o)}
        className="flex w-full items-center gap-2.5 px-4 py-3 text-left"
      >
        {done ? (
          <Check className="size-4 text-emerald-400" />
        ) : (
          <Loader2 className="size-4 animate-spin text-emerald-400" />
        )}
        <span className="text-sm font-medium text-white">
          {done ? "Reasoning complete" : "Researching & Reasoning…"}
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
        <ol className="space-y-3 border-t border-white/10 px-4 py-3">
          {steps.map((s, i) => {
            const state = i < activeIndex || done ? "done" : i === activeIndex ? "active" : "idle";
            return (
              <li
                key={s.label}
                className={`flex gap-3 text-sm transition-opacity ${state === "idle" ? "opacity-35" : ""}`}
              >
                <span className="mt-0.5 text-base leading-none">{s.icon}</span>
                <div className="min-w-0">
                  <p
                    className={`font-medium ${
                      state === "active" ? "text-white" : "text-neutral-300"
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
              </li>
            );
          })}
        </ol>
      )}
    </div>
  );
}
