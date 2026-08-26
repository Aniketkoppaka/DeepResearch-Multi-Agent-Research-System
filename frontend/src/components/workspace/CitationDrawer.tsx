'use client';

import React from 'react';

export interface CitationData {
  tag: string;
  source_title: string;
  source_url?: string;
  credibility_score: number;
  quote_snippet?: string;
  claim_type?: string;
}

export interface CitationDrawerProps {
  citation: CitationData | null;
  onClose: () => void;
}

export function CitationDrawer({ citation, onClose }: CitationDrawerProps) {
  if (!citation) return null;

  return (
    <div className="fixed inset-y-0 right-0 w-96 bg-gray-900 border-l border-gray-800 shadow-2xl p-6 z-50 overflow-y-auto">
      <div className="flex items-center justify-between pb-4 border-b border-gray-800">
        <div className="flex items-center gap-2">
          <span className="px-2 py-0.5 bg-blue-500/20 text-blue-400 font-mono text-xs font-bold rounded">
            {citation.tag}
          </span>
          <span className="text-sm font-semibold text-gray-200">Citation Explorer</span>
        </div>
        <button
          onClick={onClose}
          className="text-gray-400 hover:text-gray-200 p-1 rounded hover:bg-gray-800"
        >
          ✕
        </button>
      </div>

      <div className="mt-6 space-y-6">
        {/* Source Title & URL */}
        <div>
          <span className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Source</span>
          <h4 className="text-base font-semibold text-gray-100 mt-1">{citation.source_title}</h4>
          {citation.source_url && (
            <a
              href={citation.source_url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-xs text-blue-400 hover:underline break-all block mt-1"
            >
              {citation.source_url}
            </a>
          )}
        </div>

        {/* Credibility Score Badge */}
        <div>
          <span className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Credibility Rating</span>
          <div className="mt-1.5 flex items-center gap-2">
            <div className="px-3 py-1 bg-emerald-500/10 border border-emerald-500/30 rounded-lg text-emerald-400 font-semibold text-sm">
              {(citation.credibility_score * 100).toFixed(0)}% Score
            </div>
            <span className="text-xs text-gray-400">Verified institutional or academic authority</span>
          </div>
        </div>

        {/* Claim Type */}
        {citation.claim_type && (
          <div>
            <span className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Claim Classification</span>
            <div className="mt-1">
              <span className="px-2.5 py-1 bg-gray-800 text-xs font-mono text-gray-300 rounded border border-gray-700">
                {citation.claim_type}
              </span>
            </div>
          </div>
        )}

        {/* Exact Quote */}
        {citation.quote_snippet && (
          <div>
            <span className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Supporting Passage</span>
            <blockquote className="mt-1.5 p-3 bg-gray-950/80 border-l-2 border-blue-500 rounded-r text-xs text-gray-300 italic leading-relaxed">
              &ldquo;{citation.quote_snippet}&rdquo;
            </blockquote>
          </div>
        )}
      </div>
    </div>
  );
}
