import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { KnowledgeGraphCanvas } from '@/components/research/KnowledgeGraphCanvas';
import { CITATIONS } from '@/lib/research-data';

describe('KnowledgeGraphCanvas Component', () => {
  it('renders graph nodes, filter controls, and zoom buttons correctly', () => {
    render(<KnowledgeGraphCanvas citations={CITATIONS} />);

    expect(screen.getByText('Claim Filter:')).toBeDefined();
    expect(screen.getByText('EKG')).toBeDefined();
    expect(screen.getByTitle('Zoom In')).toBeDefined();
    expect(screen.getByTitle('Zoom Out')).toBeDefined();
  });

  it('filters nodes when selecting specific claim type', () => {
    render(<KnowledgeGraphCanvas citations={CITATIONS} />);

    const select = screen.getByRole('combobox');
    fireEvent.change(select, { target: { value: 'STATISTIC' } });

    expect(screen.getByText('Statistic')).toBeDefined();
  });
});
