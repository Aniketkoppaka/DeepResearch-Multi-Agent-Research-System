import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { PlanReviewCard } from '@/components/research/PlanReviewCard';
import { PLAN } from '@/lib/research-data';

describe('PlanReviewCard Component with Search Query Interceptor', () => {
  it('renders research questions and search query tags', () => {
    render(
      <PlanReviewCard
        plan={PLAN}
        decided={null}
        onApprove={vi.fn()}
        onRefine={vi.fn()}
      />
    );

    expect(screen.getByText(/Targeted Search Queries/i)).toBeDefined();
    expect(screen.getByText('multi-agent prompt injection defense benchmarks 2025')).toBeDefined();
  });

  it('allows adding and removing custom search queries and passes them to onApprove', () => {
    const handleApprove = vi.fn();
    render(
      <PlanReviewCard
        plan={PLAN}
        decided={null}
        onApprove={handleApprove}
        onRefine={vi.fn()}
      />
    );

    // Click Add Query
    const addBtn = screen.getByRole('button', { name: /Add Query/i });
    fireEvent.click(addBtn);

    const input = screen.getByPlaceholderText(/NIST PQC ML-KEM/i);
    fireEvent.change(input, { target: { value: 'quantum repeater latency benchmarks' } });
    
    const saveBtn = screen.getByRole('button', { name: /^Add$/i });
    fireEvent.click(saveBtn);

    expect(screen.getByText('quantum repeater latency benchmarks')).toBeDefined();

    // Click Approve
    const approveBtn = screen.getByRole('button', { name: /Approve & Begin Research/i });
    fireEvent.click(approveBtn);

    expect(handleApprove).toHaveBeenCalledOnce();
    const approvedQueries = handleApprove.mock.calls[0][0];
    expect(approvedQueries).toContain('quantum repeater latency benchmarks');
  });
});
