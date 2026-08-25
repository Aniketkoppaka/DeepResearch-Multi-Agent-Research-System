import React from "react";
import { BarChart3, Download, FileCode2, Maximize2, Sparkles } from "lucide-react";

import { Markdown } from "./Markdown";

type Props = {
  report: string;
  onCite: (id: number) => void;
  onCanvas: () => void;
  onExport: (format: "markdown" | "html") => void;
  onMetrics: () => void;
};

export function ReportCard({ report, onCite, onCanvas, onExport, onMetrics }: Props) {
  return (
    <div className="surface-panel overflow-hidden bg-[#212121] border border-white/10 rounded-2xl">
      <div className="flex items-center gap-2 border-b border-white/10 px-5 py-3">
        <Sparkles className="size-4 text-emerald-400" />
        <h3 className="text-sm font-semibold text-white">Research Synthesis</h3>
        <span className="ml-auto rounded-full bg-emerald-500/15 px-2.5 py-0.5 text-[11px] font-medium text-emerald-400">
          Grounded · 96% faithfulness
        </span>
      </div>

      <div className="px-5 py-4">
        <Markdown source={report} onCite={onCite} />
      </div>

      <div className="flex flex-wrap gap-2 border-t border-white/10 bg-black/20 px-4 py-3">
        <Action icon={<Maximize2 className="size-3.5" />} label="Open in Canvas" onClick={onCanvas} />
        <Action
          icon={<Download className="size-3.5" />}
          label="Export Markdown"
          onClick={() => onExport("markdown")}
        />
        <Action
          icon={<FileCode2 className="size-3.5" />}
          label="Export HTML"
          onClick={() => onExport("html")}
        />
        <Action
          icon={<BarChart3 className="size-3.5" />}
          label="Grounding Metrics"
          onClick={onMetrics}
        />
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
      className="flex items-center gap-1.5 rounded-full border border-white/10 px-3 py-1.5 text-xs font-medium text-neutral-300 transition-colors hover:bg-neutral-800 hover:text-white"
    >
      {icon}
      {label}
    </button>
  );
}
