'use client';

import React from 'react';

export interface AgentMetricDetail {
  tokens: number;
  cost_usd: number;
  latency_ms: number;
}

export interface WorkspaceMetrics {
  id: string;
  faithfulness_score: number;
  answer_relevance_score: number;
  context_precision_score: number;
  total_tokens: number;
  total_cost_usd: number;
  agent_token_breakdown: Record<string, AgentMetricDetail>;
  evaluation_details: Record<string, any>;
  created_at: string;
}

export interface MetricsTabProps {
  workspaceId: string;
  metrics: WorkspaceMetrics | null;
  onRunEvaluation: () => Promise<void>;
  isLoading?: boolean;
}

export function MetricsTab({
  workspaceId,
  metrics,
  onRunEvaluation,
  isLoading = false,
}: MetricsTabProps) {
  if (!metrics) {
    return (
      <div className="flex flex-col items-center justify-center p-12 text-center bg-gray-900/50 rounded-xl border border-gray-800">
        <div className="w-16 h-16 mb-4 rounded-full bg-emerald-500/10 flex items-center justify-center text-emerald-400">
          <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
        </div>
        <h3 className="text-xl font-semibold text-gray-100 mb-2">No Grounding Evaluation Executed</h3>
        <p className="text-gray-400 max-w-md mb-6">
          Compute Ragas grounding scores (Faithfulness, Answer Relevance) and analyze token/cost distribution across all subagents.
        </p>
        <button
          onClick={onRunEvaluation}
          disabled={isLoading}
          className="px-6 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white font-medium rounded-lg shadow transition disabled:opacity-50"
        >
          {isLoading ? 'Computing Metrics...' : 'Run Ragas Evaluation'}
        </button>
      </div>
    );
  }

  const ragasCards = [
    {
      title: 'Faithfulness',
      score: metrics.faithfulness_score,
      desc: 'Hallucination defense & grounded fact verification',
      color: 'text-emerald-400',
      bg: 'bg-emerald-500/10',
      border: 'border-emerald-500/20',
    },
    {
      title: 'Answer Relevance',
      score: metrics.answer_relevance_score,
      desc: 'Direct alignment with research questions & plan',
      color: 'text-blue-400',
      bg: 'bg-blue-500/10',
      border: 'border-blue-500/20',
    },
    {
      title: 'Context Precision',
      score: metrics.context_precision_score,
      desc: 'Signal-to-noise ratio in retrieved evidence passages',
      color: 'text-purple-400',
      bg: 'bg-purple-500/10',
      border: 'border-purple-500/20',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Top Banner & Trigger Button */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 p-4 bg-gray-900/60 border border-gray-800 rounded-xl">
        <div>
          <span className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Evaluation & Analytics</span>
          <h2 className="text-lg font-bold text-gray-100 mt-0.5">Ragas Grounding & Cost Telemetry</h2>
        </div>
        <button
          onClick={onRunEvaluation}
          disabled={isLoading}
          className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-medium rounded-lg shadow transition disabled:opacity-50"
        >
          {isLoading ? 'Re-evaluating...' : 'Re-Run Evaluation'}
        </button>
      </div>

      {/* Ragas Metric Gauges */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {ragasCards.map((card, i) => (
          <div
            key={i}
            className={`p-6 rounded-xl border ${card.border} ${card.bg} flex flex-col justify-between`}
          >
            <div>
              <span className="text-xs font-semibold text-gray-400 uppercase tracking-wider">{card.title}</span>
              <div className={`text-4xl font-bold font-mono mt-2 ${card.color}`}>
                {(card.score * 100).toFixed(1)}%
              </div>
            </div>
            <p className="text-xs text-gray-400 mt-4 leading-relaxed">{card.desc}</p>
          </div>
        ))}
      </div>

      {/* Overall Token & Cost Banner */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="p-6 bg-gray-900/60 border border-gray-800 rounded-xl">
          <span className="text-xs font-semibold text-gray-400 uppercase">Total Model Tokens</span>
          <div className="text-3xl font-bold font-mono text-gray-100 mt-1">
            {metrics.total_tokens.toLocaleString()}
          </div>
          <span className="text-xs text-gray-500 mt-1 block">Prompt & completion across all agent tasks</span>
        </div>
        <div className="p-6 bg-gray-900/60 border border-gray-800 rounded-xl">
          <span className="text-xs font-semibold text-gray-400 uppercase">Estimated Total Cost</span>
          <div className="text-3xl font-bold font-mono text-emerald-400 mt-1">
            ${metrics.total_cost_usd.toFixed(4)}
          </div>
          <span className="text-xs text-gray-500 mt-1 block">Standard model inference pricing</span>
        </div>
      </div>

      {/* Agent Breakdown Table */}
      {metrics.agent_token_breakdown && Object.keys(metrics.agent_token_breakdown).length > 0 && (
        <div className="p-6 bg-gray-900/60 border border-gray-800 rounded-xl">
          <h3 className="text-sm font-semibold text-gray-200 mb-4">Subagent Telemetry Breakdown</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="text-gray-400 border-b border-gray-800">
                <tr>
                  <th className="pb-3 font-semibold">Agent Role</th>
                  <th className="pb-3 font-semibold">Tokens</th>
                  <th className="pb-3 font-semibold">Cost (USD)</th>
                  <th className="pb-3 font-semibold">Avg Latency</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-800/60 text-gray-300">
                {Object.entries(metrics.agent_token_breakdown).map(([agent, data], idx) => (
                  <tr key={idx} className="hover:bg-gray-800/30">
                    <td className="py-3 font-mono font-medium text-gray-200 uppercase">{agent}</td>
                    <td className="py-3 font-mono">{data.tokens.toLocaleString()}</td>
                    <td className="py-3 font-mono text-emerald-400">${data.cost_usd.toFixed(4)}</td>
                    <td className="py-3 font-mono text-gray-400">{data.latency_ms}ms</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
