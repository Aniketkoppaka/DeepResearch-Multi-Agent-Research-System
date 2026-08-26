import React, { useState } from "react";
import {
  BarChart3,
  Download,
  FileCode2,
  FileText,
  Maximize2,
  Network,
  Sparkles,
  Copy,
  Check,
  LayoutTemplate,
} from "lucide-react";

import { Markdown } from "./Markdown";
import { REPORT_TEMPLATES } from "@/lib/research-data";

type Props = {
  report: string;
  onCite: (id: number) => void;
  onCanvas: () => void;
  onGraph: () => void;
  onExport: (format: "markdown" | "html" | "pdf") => void;
  onMetrics: () => void;
};

export function ReportCard({ report, onCite, onCanvas, onGraph, onExport, onMetrics }: Props) {
  const [selectedTemplate, setSelectedTemplate] = useState<"academic" | "executive" | "technical">("academic");
  const [copied, setCopied] = useState(false);

  const activeContent = REPORT_TEMPLATES[selectedTemplate]?.markdown || report;

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(activeContent);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (_) {}
  };

  return (
    <div className="surface-panel overflow-hidden bg-[#212121] border border-white/10 rounded-2xl shadow-xl">
      {/* Header with Title and Verification Pill */}
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-white/10 px-5 py-3 bg-neutral-900/40">
        <div className="flex items-center gap-2">
          <Sparkles className="size-4 text-emerald-400" />
          <h3 className="text-sm font-semibold text-white">Research Synthesis</h3>
        </div>

        <div className="flex items-center gap-2">
          {/* Template Selector Pills */}
          <div className="flex items-center bg-[#171717] rounded-xl p-0.5 border border-white/10 text-xs">
            {(Object.keys(REPORT_TEMPLATES) as Array<"academic" | "executive" | "technical">).map((key) => {
              const active = selectedTemplate === key;
              return (
                <button
                  key={key}
                  onClick={() => setSelectedTemplate(key)}
                  className={`px-2.5 py-1 rounded-lg font-medium transition-colors cursor-pointer text-[11px] ${
                    active
                      ? "bg-emerald-600 text-white shadow-sm"
                      : "text-neutral-400 hover:text-neutral-200"
                  }`}
                >
                  {REPORT_TEMPLATES[key].label}
                </button>
              );
            })}
          </div>

          <span className="rounded-full bg-emerald-500/15 px-2.5 py-1 text-[11px] font-medium text-emerald-400">
            96% faithfulness
          </span>
        </div>
      </div>

      {/* Rendered Markdown with Inline Citations */}
      <div className="px-5 py-4">
        <Markdown source={activeContent} onCite={onCite} />
      </div>

      {/* Multi-Format Actions Footer */}
      <div className="flex flex-wrap items-center justify-between gap-2 border-t border-white/10 bg-black/20 px-4 py-3">
        <div className="flex flex-wrap gap-2">
          <Action icon={<Network className="size-3.5 text-emerald-400" />} label="Knowledge Graph (EKG)" onClick={onGraph} />
          <Action icon={<Maximize2 className="size-3.5" />} label="Open in Canvas" onClick={onCanvas} />
          <Action icon={<BarChart3 className="size-3.5" />} label="Grounding Metrics" onClick={onMetrics} />
        </div>

        <div className="flex flex-wrap items-center gap-1.5">
          <button
            onClick={handleCopy}
            title="Copy formatted markdown"
            className="flex items-center gap-1.5 rounded-lg border border-white/10 bg-neutral-900/60 px-2.5 py-1.5 text-xs font-medium text-neutral-300 hover:bg-neutral-800 hover:text-white cursor-pointer transition-colors"
          >
            {copied ? <Check className="size-3.5 text-emerald-400" /> : <Copy className="size-3.5" />}
            <span>{copied ? "Copied!" : "Copy"}</span>
          </button>

          <Action
            icon={<Download className="size-3.5" />}
            label="Markdown"
            onClick={() => onExport("markdown")}
          />
          <Action
            icon={<FileCode2 className="size-3.5" />}
            label="HTML"
            onClick={() => onExport("html")}
          />
          <Action
            icon={<FileText className="size-3.5 text-red-400" />}
            label="PDF"
            onClick={() => onExport("pdf")}
          />
        </div>
      </div>
    </div>
  );
}

function Action({
  icon,
  label,
  onClick,
}: {
  icon: React.ReactNode;
  label: string;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className="flex items-center gap-1.5 rounded-lg border border-white/10 bg-neutral-900/40 px-2.5 py-1.5 text-xs font-medium text-neutral-300 transition-colors hover:bg-neutral-800 hover:text-white cursor-pointer"
    >
      {icon}
      {label}
    </button>
  );
}
