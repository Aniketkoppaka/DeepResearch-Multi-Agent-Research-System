'use client';

import React, { useState } from 'react';

export interface ResearchPlan {
  title: string;
  objectives: string[];
  research_questions: string[];
  hypotheses: string[];
  search_strategy: Record<string, any>;
  expected_sources: string[];
  deliverables: string[];
}

export interface PlanTabProps {
  workspaceId: string;
  planStatus: 'draft' | 'pending_approval' | 'approved' | 'rejected';
  plan: ResearchPlan | null;
  onGeneratePlan: () => Promise<void>;
  onApprovePlan: () => Promise<void>;
  onRejectPlan: (feedback: string) => Promise<void>;
  isLoading?: boolean;
}

export function PlanTab({
  workspaceId,
  planStatus,
  plan,
  onGeneratePlan,
  onApprovePlan,
  onRejectPlan,
  isLoading = false,
}: PlanTabProps) {
  const [feedback, setFeedback] = useState('');
  const [isRejecting, setIsRejecting] = useState(false);

  if (!plan || planStatus === 'draft') {
    return (
      <div className="flex flex-col items-center justify-center p-12 text-center bg-gray-900/50 rounded-xl border border-gray-800">
        <div className="w-16 h-16 mb-4 rounded-full bg-blue-500/10 flex items-center justify-center text-blue-400">
          <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
          </svg>
        </div>
        <h3 className="text-xl font-semibold text-gray-100 mb-2">No Research Plan Generated Yet</h3>
        <p className="text-gray-400 max-w-md mb-6">
          The Planner Agent will formulate clear research questions, search strategies, and deliverables before execution starts.
        </p>
        <button
          onClick={onGeneratePlan}
          disabled={isLoading}
          className="px-6 py-2.5 bg-blue-600 hover:bg-blue-500 text-white font-medium rounded-lg shadow transition disabled:opacity-50"
        >
          {isLoading ? 'Generating Plan...' : 'Generate Research Plan'}
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Approval Status Alert */}
      {planStatus === 'pending_approval' && (
        <div className="p-4 bg-amber-500/10 border border-amber-500/30 rounded-xl flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div>
            <span className="inline-block px-2.5 py-0.5 text-xs font-semibold bg-amber-500/20 text-amber-300 rounded-full mb-1">
              ACTION REQUIRED
            </span>
            <h4 className="text-gray-100 font-medium">Review and Approve Research Plan</h4>
            <p className="text-sm text-gray-400">
              Execution is blocked until you review the objectives and approve the research scope.
            </p>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={() => setIsRejecting(true)}
              disabled={isLoading}
              className="px-4 py-2 bg-gray-800 hover:bg-gray-700 text-gray-300 text-sm font-medium rounded-lg transition"
            >
              Request Changes
            </button>
            <button
              onClick={onApprovePlan}
              disabled={isLoading}
              className="px-5 py-2 bg-emerald-600 hover:bg-emerald-500 text-white text-sm font-medium rounded-lg shadow transition"
            >
              {isLoading ? 'Approving...' : 'Approve & Begin Research'}
            </button>
          </div>
        </div>
      )}

      {planStatus === 'approved' && (
        <div className="p-4 bg-emerald-500/10 border border-emerald-500/30 rounded-xl flex items-center gap-3">
          <svg className="w-5 h-5 text-emerald-400 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
          <div>
            <span className="text-sm font-semibold text-emerald-300">Plan Approved</span>
            <p className="text-xs text-gray-400">Agents are executing research according to this approved strategy.</p>
          </div>
        </div>
      )}

      {/* Reject / Request Changes Modal */}
      {isRejecting && (
        <div className="p-4 bg-gray-900 border border-gray-700 rounded-xl space-y-3">
          <h4 className="text-sm font-semibold text-gray-200">What would you like the Planner to change?</h4>
          <textarea
            value={feedback}
            onChange={(e) => setFeedback(e.target.value)}
            placeholder="E.g., Focus more on commercial applications, restrict search to papers published after 2023..."
            className="w-full h-24 p-3 bg-gray-950 border border-gray-800 rounded-lg text-sm text-gray-200 focus:outline-none focus:border-blue-500"
          />
          <div className="flex justify-end gap-2">
            <button
              onClick={() => setIsRejecting(false)}
              className="px-3 py-1.5 text-xs text-gray-400 hover:text-gray-200"
            >
              Cancel
            </button>
            <button
              onClick={async () => {
                await onRejectPlan(feedback);
                setIsRejecting(false);
                setFeedback('');
              }}
              disabled={!feedback.trim() || isLoading}
              className="px-4 py-1.5 bg-blue-600 hover:bg-blue-500 text-white text-xs font-medium rounded-md disabled:opacity-50"
            >
              Submit Refinement
            </button>
          </div>
        </div>
      )}

      {/* Plan Card */}
      <div className="p-6 bg-gray-900/60 border border-gray-800 rounded-xl space-y-6">
        <div>
          <span className="text-xs font-semibold text-blue-400 uppercase tracking-wider">Research Plan</span>
          <h2 className="text-2xl font-bold text-gray-100 mt-1">{plan.title}</h2>
        </div>

        {/* Objectives */}
        <div>
          <h3 className="text-sm font-semibold text-gray-300 mb-2">Core Objectives</h3>
          <ul className="space-y-1.5">
            {plan.objectives.map((obj, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-gray-300">
                <span className="w-1.5 h-1.5 rounded-full bg-blue-500 mt-2 shrink-0" />
                <span>{obj}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Research Questions */}
        <div>
          <h3 className="text-sm font-semibold text-gray-300 mb-2">Key Research Questions</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {plan.research_questions.map((q, i) => (
              <div key={i} className="p-3 bg-gray-950/60 border border-gray-800/80 rounded-lg text-sm text-gray-300">
                <span className="text-xs font-mono text-blue-400 block mb-1">RQ {i + 1}</span>
                {q}
              </div>
            ))}
          </div>
        </div>

        {/* Hypotheses */}
        {plan.hypotheses && plan.hypotheses.length > 0 && (
          <div>
            <h3 className="text-sm font-semibold text-gray-300 mb-2">Initial Hypotheses</h3>
            <ul className="space-y-1.5">
              {plan.hypotheses.map((hyp, i) => (
                <li key={i} className="flex items-start gap-2 text-sm text-gray-400 italic">
                  <span className="text-amber-400 font-mono text-xs">H{i + 1}:</span>
                  <span>{hyp}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Deliverables */}
        {plan.deliverables && plan.deliverables.length > 0 && (
          <div>
            <h3 className="text-sm font-semibold text-gray-300 mb-2">Expected Deliverables</h3>
            <div className="flex flex-wrap gap-2">
              {plan.deliverables.map((del, i) => (
                <span key={i} className="px-3 py-1 bg-gray-800 text-xs text-gray-300 rounded-md border border-gray-700">
                  {del}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
