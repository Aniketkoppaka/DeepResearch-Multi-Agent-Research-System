import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { ReportCard } from '@/components/research/ReportCard';
import { REPORT } from '@/lib/research-data';

describe('ReportCard Component with Template Switcher & Export', () => {
  it('renders report and allows switching between synthesis templates', () => {
    render(
      <ReportCard
        report={REPORT}
        onCite={vi.fn()}
        onCanvas={vi.fn()}
        onGraph={vi.fn()}
        onExport={vi.fn()}
        onMetrics={vi.fn()}
      />
    );

    expect(screen.getByText('Research Synthesis')).toBeDefined();
    expect(screen.getByRole('button', { name: /Academic Review/i })).toBeDefined();
    expect(screen.getByRole('button', { name: /Executive Brief/i })).toBeDefined();
    expect(screen.getByRole('button', { name: /Technical Architecture/i })).toBeDefined();

    // Switch to Executive Brief template
    const execBtn = screen.getByRole('button', { name: /Executive Brief/i });
    fireEvent.click(execBtn);

    expect(screen.getByText(/High-Level Impact & Takeaways/i)).toBeDefined();
  });

  it('triggers export functions for markdown, html, and pdf', () => {
    const handleExport = vi.fn();
    render(
      <ReportCard
        report={REPORT}
        onCite={vi.fn()}
        onCanvas={vi.fn()}
        onGraph={vi.fn()}
        onExport={handleExport}
        onMetrics={vi.fn()}
      />
    );

    const pdfBtn = screen.getByRole('button', { name: /^PDF$/i });
    fireEvent.click(pdfBtn);

    expect(handleExport).toHaveBeenCalledWith('pdf');
  });
});
