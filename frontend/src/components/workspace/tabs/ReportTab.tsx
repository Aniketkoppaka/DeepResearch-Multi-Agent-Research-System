'use client';

import React, { useState } from 'react';
import { CitationData, CitationDrawer } from '../CitationDrawer';

export interface ReportVersion {
  id: string;
  version_number: number;
  title: string;
  markdown_content: string;
  citations_json: Record<string, CitationData>;
  created_at: string;
}

export interface ReportTabProps {
  workspaceId: string;
  reports: ReportVersion[];
  onGenerateReport: () => Promise<void>;
  isLoading?: boolean;
}

export function ReportTab({
  workspaceId,
  reports,
  onGenerateReport,
  isLoading = false,
}: ReportTabProps) {
  const [selectedVersion, setSelectedVersion] = useState<number>(
    reports.length > 0 ? reports[0].version_number : 1
  );
  const [activeCitation, setActiveCitation] = useState<CitationData | null>(null);

  const currentReport = reports.find((r) => r.version_number === selectedVersion) || reports[0];

  if (!reports || reports.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center p-12 text-center bg-gray-900/50 rounded-xl border border-gray-800">
        <div className="w-16 h-16 mb-4 rounded-full bg-purple-500/10 flex items-center justify-center text-purple-400">
          <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
          </svg>
        </div>
        <h3 className="text-xl font-semibold text-gray-100 mb-2">No Research Report Synthesized</h3>
        <p className="text-gray-400 max-w-md mb-6">
          The Synthesizer Agent will weave all extracted evidence nodes, credibility ratings, and findings into a publication-grade report with inline citations.
        </p>
        <button
          onClick={onGenerateReport}
          disabled={isLoading}
          className="px-6 py-2.5 bg-purple-600 hover:bg-purple-500 text-white font-medium rounded-lg shadow transition disabled:opacity-50"
        >
          {isLoading ? 'Synthesizing Report...' : 'Synthesize Research Report'}
        </button>
      </div>
    );
  }

  // Render markdown text with clickable inline citations
  const renderFormattedContent = (content: string) => {
    const parts = content.split(/(\[\d+\])/g);
    return parts.map((part, index) => {
      const match = part.match(/^\[(\d+)\]$/);
      if (match) {
        const citationMeta = currentReport.citations_json[part];
        return (
          <button
            key={index}
            onClick={() => setActiveCitation(citationMeta || { tag: part, source_title: 'Cited Source', credibility_score: 0.8 })}
            className="inline-flex items-center px-1 text-xs font-semibold font-mono text-blue-400 bg-blue-500/10 hover:bg-blue-500/20 rounded mx-0.5 transition cursor-pointer"
          >
            {part}
          </button>
        );
      }
      return <span key={index}>{part}</span>;
    });
  };

  return (
    <div className="space-y-6">
      {/* Header with Version Selector & Export Buttons */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 p-4 bg-gray-900/60 border border-gray-800 rounded-xl">
        <div className="flex items-center gap-3">
          <span className="text-xs font-semibold text-gray-400 uppercase">Version:</span>
          <select
            value={currentReport.version_number}
            onChange={(e) => setSelectedVersion(Number(e.target.value))}
            className="bg-gray-950 border border-gray-800 text-gray-200 text-sm rounded-lg px-3 py-1.5 focus:outline-none focus:border-blue-500"
          >
            {reports.map((r) => (
              <option key={r.version_number} value={r.version_number}>
                Version {r.version_number}
              </option>
            ))}
          </select>
          <span className="text-xs text-gray-500">
            Created on {new Date(currentReport.created_at).toLocaleDateString()}
          </span>
        </div>

        <div className="flex items-center gap-2">
          <a
            href={`/api/v1/workspaces/${workspaceId}/reports/${currentReport.id}/export?format=markdown`}
            className="px-3.5 py-1.5 bg-gray-800 hover:bg-gray-700 text-gray-300 text-xs font-medium rounded-lg transition"
            download
          >
            Export Markdown
          </a>
          <a
            href={`/api/v1/workspaces/${workspaceId}/reports/${currentReport.id}/export?format=html`}
            className="px-3.5 py-1.5 bg-gray-800 hover:bg-gray-700 text-gray-300 text-xs font-medium rounded-lg transition"
            download
          >
            Export HTML
          </a>
          <button
            onClick={onGenerateReport}
            disabled={isLoading}
            className="px-4 py-1.5 bg-purple-600 hover:bg-purple-500 text-white text-xs font-medium rounded-lg shadow transition"
          >
            {isLoading ? 'Re-synthesizing...' : 'Re-synthesize'}
          </button>
        </div>
      </div>

      {/* Report Document Content */}
      <div className="p-8 bg-gray-900/60 border border-gray-800 rounded-xl prose prose-invert max-w-none">
        <h1 className="text-2xl font-bold text-gray-100 mb-6">{currentReport.title}</h1>
        <div className="whitespace-pre-line text-sm text-gray-300 leading-relaxed font-sans">
          {renderFormattedContent(currentReport.markdown_content)}
        </div>
      </div>

      {/* Citation Explorer Drawer */}
      <CitationDrawer
        citation={activeCitation}
        onClose={() => setActiveCitation(null)}
      />
    </div>
  );
}
