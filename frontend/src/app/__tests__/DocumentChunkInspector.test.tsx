import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { DocumentChunkInspector, SAMPLE_CHUNKS } from '@/components/research/DocumentChunkInspector';

describe('DocumentChunkInspector Component', () => {
  it('renders document ingestion summary, chunks count, and section headings', () => {
    render(
      <DocumentChunkInspector
        documentName="sample_research_doc.pdf"
        chunks={SAMPLE_CHUNKS}
      />
    );

    expect(screen.getByText('sample_research_doc.pdf')).toBeDefined();
    expect(screen.getByText(/4 chunks indexed/i)).toBeDefined();
    expect(screen.getByText('Executive Summary')).toBeDefined();
    expect(screen.getByText('1. NIST Standardization: ML-KEM and ML-DSA')).toBeDefined();
  });

  it('filters chunks when entering keyword or search terms', () => {
    render(
      <DocumentChunkInspector
        documentName="sample_research_doc.pdf"
        chunks={SAMPLE_CHUNKS}
      />
    );

    const input = screen.getByPlaceholderText(/Filter semantic chunks/i);
    fireEvent.change(input, { target: { value: 'repeater' } });

    expect(screen.getByText('2. Quantum Key Distribution Realities and Challenges')).toBeDefined();
  });
});
