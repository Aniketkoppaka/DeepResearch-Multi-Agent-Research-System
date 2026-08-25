import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { MetricsTab, WorkspaceMetrics } from '../../components/workspace/tabs/MetricsTab';

const mockMetrics: WorkspaceMetrics = {
  id: 'metric-123',
  faithfulness_score: 0.95,
  answer_relevance_score: 0.92,
  context_precision_score: 0.88,
  total_tokens: 12500,
  total_cost_usd: 0.0452,
  agent_token_breakdown: {
    planner: { tokens: 2300, cost_usd: 0.008, latency_ms: 1200 },
    synthesizer: { tokens: 5500, cost_usd: 0.021, latency_ms: 3100 },
  },
  evaluation_details: {},
  created_at: '2026-08-26T00:00:00Z',
};

describe('MetricsTab Component', () => {
  it('renders empty state button when metrics is null', () => {
    const handleRun = vi.fn();
    render(
      <MetricsTab
        workspaceId="ws-1"
        metrics={null}
        onRunEvaluation={handleRun}
      />
    );

    expect(screen.getByText('No Grounding Evaluation Executed')).toBeDefined();
    const btn = screen.getByRole('button', { name: /Run Ragas Evaluation/i });
    fireEvent.click(btn);
    expect(handleRun).toHaveBeenCalledOnce();
  });

  it('renders scores and telemetry breakdown', () => {
    render(
      <MetricsTab
        workspaceId="ws-1"
        metrics={mockMetrics}
        onRunEvaluation={vi.fn()}
      />
    );

    expect(screen.getByText('95.0%')).toBeDefined();
    expect(screen.getByText('92.0%')).toBeDefined();
    expect(screen.getByText('12,500')).toBeDefined();
    expect(screen.getByText('$0.0452')).toBeDefined();
    expect(screen.getByText(/planner/i)).toBeDefined();
    expect(screen.getByText(/synthesizer/i)).toBeDefined();
  });
});

