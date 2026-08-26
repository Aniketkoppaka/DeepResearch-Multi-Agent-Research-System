import React, { useState, useMemo } from "react";
import {
  Network,
  BadgeCheck,
  AlertTriangle,
  ExternalLink,
  Filter,
  ZoomIn,
  ZoomOut,
  RotateCcw,
  Sparkles,
} from "lucide-react";
import type { Citation } from "@/lib/research-data";

export type GraphNode = {
  id: string;
  label: string;
  type: "source" | "claim";
  claimType?: Citation["claim"];
  credibility?: number;
  credibilityLabel?: string;
  quote?: string;
  url?: string;
  publisher?: string;
  verified?: boolean;
  contradiction?: string;
  x: number;
  y: number;
};

export type GraphEdge = {
  id: string;
  source: string;
  target: string;
  type: "SUPPORTS" | "CONTRADICTS" | "EXTRACTED_FROM" | "CITES";
  label?: string;
};

const CLAIM_COLORS: Record<Citation["claim"], { bg: string; border: string; text: string }> = {
  FACT: { bg: "#064e3b", border: "#10b981", text: "#6ee7b7" },
  FINDING: { bg: "#1e3a8a", border: "#3b82f6", text: "#93c5fd" },
  STATISTIC: { bg: "#581c87", border: "#a855f7", text: "#d8b4fe" },
  HYPOTHESIS: { bg: "#78350f", border: "#f59e0b", text: "#fcd34d" },
};

type Props = {
  citations: Citation[];
  onSelectCitation?: (id: number) => void;
};

export function KnowledgeGraphCanvas({ citations, onSelectCitation }: Props) {
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [filterClaimType, setFilterClaimType] = useState<string>("ALL");
  const [zoom, setZoom] = useState(1);

  // Generate deterministic graph data from citations and claims
  const { nodes, edges } = useMemo(() => {
    const n: GraphNode[] = [];
    const e: GraphEdge[] = [];

    // Root Topic Node
    n.push({
      id: "root",
      label: "Research Investigation",
      type: "source",
      verified: true,
      x: 300,
      y: 200,
    });

    citations.forEach((c, idx) => {
      const angle = (idx / citations.length) * 2 * Math.PI - Math.PI / 2;
      const radius = 130;
      const sourceX = 300 + Math.cos(angle) * radius;
      const sourceY = 200 + Math.sin(angle) * radius;

      const sourceId = `src-${c.id}`;
      n.push({
        id: sourceId,
        label: c.publisher || `Source [${c.id}]`,
        type: "source",
        credibility: c.credibility,
        credibilityLabel: c.credibilityLabel,
        url: c.url,
        publisher: c.publisher,
        verified: c.verified,
        x: sourceX,
        y: sourceY,
      });

      e.push({
        id: `e-root-${sourceId}`,
        source: "root",
        target: sourceId,
        type: "CITES",
        label: "Indexed",
      });

      // Claim Node
      const claimAngle = angle + 0.35;
      const claimRadius = 240;
      const claimX = 300 + Math.cos(claimAngle) * claimRadius;
      const claimY = 200 + Math.sin(claimAngle) * claimRadius;

      const claimId = `claim-${c.id}`;
      n.push({
        id: claimId,
        label: c.title.length > 28 ? c.title.slice(0, 26) + "…" : c.title,
        type: "claim",
        claimType: c.claim,
        credibility: c.credibility,
        quote: c.quote,
        url: c.url,
        publisher: c.publisher,
        verified: c.verified,
        contradiction: c.contradiction,
        x: claimX,
        y: claimY,
      });

      e.push({
        id: `e-${sourceId}-${claimId}`,
        source: sourceId,
        target: claimId,
        type: c.contradiction ? "CONTRADICTS" : "SUPPORTS",
        label: c.contradiction ? "Contradicts" : "Supports",
      });
    });

    return { nodes: n, edges: e };
  }, [citations]);

  const filteredNodes = useMemo(() => {
    if (filterClaimType === "ALL") return nodes;
    return nodes.filter(
      (n) => n.type === "source" || n.claimType === filterClaimType
    );
  }, [nodes, filterClaimType]);

  const filteredNodeIds = useMemo(
    () => new Set(filteredNodes.map((n) => n.id)),
    [filteredNodes]
  );

  const filteredEdges = useMemo(() => {
    return edges.filter(
      (e) => filteredNodeIds.has(e.source) && filteredNodeIds.has(e.target)
    );
  }, [edges, filteredNodeIds]);

  return (
    <div className="flex flex-col h-full bg-[#171717] rounded-xl overflow-hidden border border-white/10">
      {/* Controls Bar */}
      <div className="flex items-center justify-between px-4 py-2.5 bg-neutral-900/80 border-b border-white/10 text-xs">
        <div className="flex items-center gap-2">
          <Filter className="size-3.5 text-neutral-400" />
          <span className="text-neutral-400">Claim Filter:</span>
          <select
            aria-label="Claim Filter"
            value={filterClaimType}
            onChange={(e) => setFilterClaimType(e.target.value)}
            className="bg-[#212121] text-neutral-200 border border-white/10 rounded-md px-2 py-1 outline-none text-xs"
          >
            <option value="ALL">All Nodes</option>
            <option value="FACT">Facts</option>
            <option value="FINDING">Findings</option>
            <option value="STATISTIC">Statistics</option>
            <option value="HYPOTHESIS">Hypotheses</option>
          </select>
        </div>

        <div className="flex items-center gap-1.5">
          <button
            onClick={() => setZoom((z) => Math.min(z + 0.15, 1.8))}
            className="p-1 rounded bg-[#212121] hover:bg-neutral-800 text-neutral-300 border border-white/10"
            title="Zoom In"
          >
            <ZoomIn className="size-3.5" />
          </button>
          <button
            onClick={() => setZoom((z) => Math.max(z - 0.15, 0.6))}
            className="p-1 rounded bg-[#212121] hover:bg-neutral-800 text-neutral-300 border border-white/10"
            title="Zoom Out"
          >
            <ZoomOut className="size-3.5" />
          </button>
          <button
            onClick={() => setZoom(1)}
            className="p-1 rounded bg-[#212121] hover:bg-neutral-800 text-neutral-300 border border-white/10"
            title="Reset Zoom"
          >
            <RotateCcw className="size-3.5" />
          </button>
        </div>
      </div>

      {/* Main Visualizer Area */}
      <div className="relative flex-1 bg-[#121212] overflow-hidden flex items-center justify-center min-h-[380px]">
        <svg
          viewBox="0 0 600 400"
          className="w-full h-full cursor-grab active:cursor-grabbing transition-transform duration-150"
          style={{ transform: `scale(${zoom})` }}
        >
          <defs>
            <marker
              id="arrow-supports"
              markerWidth="8"
              markerHeight="8"
              refX="18"
              refY="4"
              orient="auto"
            >
              <polygon points="0 0, 8 4, 0 8" fill="#10b981" opacity="0.7" />
            </marker>
            <marker
              id="arrow-contradicts"
              markerWidth="8"
              markerHeight="8"
              refX="18"
              refY="4"
              orient="auto"
            >
              <polygon points="0 0, 8 4, 0 8" fill="#ef4444" opacity="0.9" />
            </marker>
            <marker
              id="arrow-cites"
              markerWidth="8"
              markerHeight="8"
              refX="18"
              refY="4"
              orient="auto"
            >
              <polygon points="0 0, 8 4, 0 8" fill="#6b7280" opacity="0.6" />
            </marker>
          </defs>

          {/* Edges */}
          {filteredEdges.map((edge) => {
            const srcNode = filteredNodes.find((n) => n.id === edge.source);
            const tgtNode = filteredNodes.find((n) => n.id === edge.target);
            if (!srcNode || !tgtNode) return null;

            const isContradiction = edge.type === "CONTRADICTS";
            const strokeColor = isContradiction
              ? "#ef4444"
              : edge.type === "SUPPORTS"
              ? "#10b981"
              : "#4b5563";

            return (
              <g key={edge.id}>
                <line
                  x1={srcNode.x}
                  y1={srcNode.y}
                  x2={tgtNode.x}
                  y2={tgtNode.y}
                  stroke={strokeColor}
                  strokeWidth={isContradiction ? 2 : 1.2}
                  strokeDasharray={isContradiction ? "4,4" : undefined}
                  opacity={0.65}
                  markerEnd={
                    isContradiction
                      ? "url(#arrow-contradicts)"
                      : edge.type === "SUPPORTS"
                      ? "url(#arrow-supports)"
                      : "url(#arrow-cites)"
                  }
                />
              </g>
            );
          })}

          {/* Nodes */}
          {filteredNodes.map((node) => {
            const isSelected = selectedNode?.id === node.id;
            const isRoot = node.id === "root";

            let fill = "#1e293b";
            let stroke = "#3b82f6";
            let textFill = "#93c5fd";

            if (isRoot) {
              fill = "#065f46";
              stroke = "#34d399";
              textFill = "#ffffff";
            } else if (node.type === "claim" && node.claimType) {
              const cfg = CLAIM_COLORS[node.claimType];
              fill = cfg.bg;
              stroke = cfg.border;
              textFill = cfg.text;
            } else if (node.type === "source") {
              fill = "#18181b";
              stroke = "#71717a";
              textFill = "#e4e4e7";
            }

            return (
              <g
                key={node.id}
                onClick={() => setSelectedNode(node)}
                className="cursor-pointer transition-transform hover:scale-105"
              >
                <circle
                  cx={node.x}
                  cy={node.y}
                  r={isRoot ? 26 : node.type === "source" ? 18 : 16}
                  fill={fill}
                  stroke={isSelected ? "#ffffff" : stroke}
                  strokeWidth={isSelected ? 2.5 : 1.5}
                  className="drop-shadow-md"
                />
                {isRoot && (
                  <text
                    x={node.x}
                    y={node.y + 4}
                    textAnchor="middle"
                    fill={textFill}
                    fontSize="9"
                    fontWeight="bold"
                  >
                    EKG
                  </text>
                )}
                {!isRoot && (
                  <text
                    x={node.x}
                    y={node.y + (node.type === "source" ? 30 : 28)}
                    textAnchor="middle"
                    fill="#d1d5db"
                    fontSize="9.5"
                    fontWeight="500"
                    className="select-none"
                  >
                    {node.label}
                  </text>
                )}
              </g>
            );
          })}
        </svg>

        {/* Selected Node Details Floating Overlay */}
        {selectedNode && (
          <div className="absolute bottom-3 left-3 right-3 bg-[#1e1e1e]/95 backdrop-blur-md border border-white/10 rounded-xl p-3 shadow-2xl text-xs">
            <div className="flex items-center justify-between pb-1.5 border-b border-white/10">
              <div className="flex items-center gap-1.5">
                <Network className="size-3.5 text-emerald-400" />
                <span className="font-semibold text-white">
                  {selectedNode.type === "source" ? "Evidence Source" : `Claim: ${selectedNode.claimType}`}
                </span>
                {selectedNode.verified && (
                  <BadgeCheck className="size-3 text-emerald-400" title="Verified source" />
                )}
              </div>
              <button
                onClick={() => setSelectedNode(null)}
                className="text-neutral-400 hover:text-white"
              >
                ✕
              </button>
            </div>

            <p className="mt-2 text-white font-medium">{selectedNode.label}</p>

            {selectedNode.quote && (
              <blockquote className="mt-1.5 p-2 bg-black/40 rounded-lg text-[11px] text-neutral-300 italic border-l-2 border-emerald-500">
                "{selectedNode.quote}"
              </blockquote>
            )}

            {selectedNode.contradiction && (
              <div className="mt-1.5 p-2 bg-red-950/40 border border-red-800/40 rounded-lg text-[11px] text-red-200 flex items-start gap-1.5">
                <AlertTriangle className="size-3 text-red-400 shrink-0 mt-0.5" />
                <span>{selectedNode.contradiction}</span>
              </div>
            )}

            <div className="mt-2 flex items-center justify-between text-[11px] text-neutral-400">
              {selectedNode.credibility && (
                <span>Credibility: <strong className="text-emerald-400 font-mono">{Math.round(selectedNode.credibility * 100)}%</strong></span>
              )}
              {selectedNode.url && (
                <a
                  href={selectedNode.url}
                  target="_blank"
                  rel="noreferrer"
                  className="text-emerald-400 hover:underline flex items-center gap-1"
                >
                  View Source <ExternalLink className="size-2.5" />
                </a>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Footer Legend */}
      <div className="px-4 py-2 bg-neutral-900/60 border-t border-white/5 flex flex-wrap gap-4 text-[10px] text-neutral-400">
        <span className="flex items-center gap-1">
          <span className="size-2 rounded-full bg-emerald-500" /> Fact
        </span>
        <span className="flex items-center gap-1">
          <span className="size-2 rounded-full bg-blue-500" /> Finding
        </span>
        <span className="flex items-center gap-1">
          <span className="size-2 rounded-full bg-purple-500" /> Statistic
        </span>
        <span className="flex items-center gap-1">
          <span className="size-2 rounded-full bg-amber-500" /> Hypothesis
        </span>
        <span className="flex items-center gap-1">
          <span className="size-2 rounded-full bg-red-500" /> Contradiction Edge
        </span>
      </div>
    </div>
  );
}
