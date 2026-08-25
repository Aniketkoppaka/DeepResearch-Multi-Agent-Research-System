import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { ReportTab, ReportVersion } from '../../components/workspace/tabs/ReportTab';

const mockReports: ReportVersion[] = [
  {
    id: 'report-1',
    version_number: 1,
    title: 'Quantum Advantage Report',
    markdown_content: 'Recent studies demonstrate quantum threshold [1] in error correction.',
    citations_json: {
      '[1]': {
        tag: '[1]',
        source_title: 'Nature Quantum Article',
        credibility_score: 0.95,
        quote_snippet: 'Quantum threshold verified.',
        claim_type: 'FINDING',
      },
    },
    created_at: '2026-08-26T00:00:00Z',
  },
];

describe('ReportTab Component', () => {
  it('renders report content and opens citation drawer on clicking inline citation tag', () => {
    render(
      <ReportTab
        workspaceId="ws-123"
        reports={mockReports}
        onGenerateReport={vi.fn()}
      />
    );

    expect(screen.getByText('Quantum Advantage Report')).toBeDefined();
    const citationBtn = screen.getByRole('button', { name: '[1]' });
    fireEvent.click(citationBtn);

    // Citation drawer should open with source title and score
    expect(screen.getByText('Citation Explorer')).toBeDefined();
    expect(screen.getByText('Nature Quantum Article')).toBeDefined();
    expect(screen.getByText('95% Score')).toBeDefined();
  });
});
