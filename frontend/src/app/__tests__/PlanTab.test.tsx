import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { PlanTab, ResearchPlan } from '../../components/workspace/tabs/PlanTab';


const mockPlan: ResearchPlan = {
  title: 'Quantum Computing Research Plan',
  objectives: ['Analyze error correction rates'],
  research_questions: ['What is the threshold limit?'],
  hypotheses: ['Threshold exceeds 99%'],
  search_strategy: { keywords: ['quantum'] },
  expected_sources: ['arXiv'],
  deliverables: ['Executive Summary'],
};

describe('PlanTab Component', () => {
  it('renders generate plan button when plan is null', () => {
    const handleGenerate = vi.fn();
    render(
      <PlanTab
        workspaceId="123"
        planStatus="draft"
        plan={null}
        onGeneratePlan={handleGenerate}
        onApprovePlan={vi.fn()}
        onRejectPlan={vi.fn()}
      />
    );

    expect(screen.getByText('No Research Plan Generated Yet')).toBeDefined();
    const btn = screen.getByRole('button', { name: /Generate Research Plan/i });
    fireEvent.click(btn);
    expect(handleGenerate).toHaveBeenCalledOnce();
  });

  it('renders pending approval action bar and triggers approval', () => {
    const handleApprove = vi.fn();
    render(
      <PlanTab
        workspaceId="123"
        planStatus="pending_approval"
        plan={mockPlan}
        onGeneratePlan={vi.fn()}
        onApprovePlan={handleApprove}
        onRejectPlan={vi.fn()}
      />
    );

    expect(screen.getByText('Quantum Computing Research Plan')).toBeDefined();
    expect(screen.getByText('Analyze error correction rates')).toBeDefined();
    const approveBtn = screen.getByRole('button', { name: /Approve & Begin Research/i });
    fireEvent.click(approveBtn);
    expect(handleApprove).toHaveBeenCalledOnce();
  });
});
