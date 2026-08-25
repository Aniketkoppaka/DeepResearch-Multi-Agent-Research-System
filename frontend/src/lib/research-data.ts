export type ResearchMode = "quick" | "deep" | "academic";

export const MODES: {
  id: ResearchMode;
  emoji: string;
  label: string;
  hint: string;
}[] = [
  { id: "quick", emoji: "⚡", label: "Quick Scan", hint: "1–2 min" },
  { id: "deep", emoji: "🔍", label: "Deep Investigation", hint: "3–5 min" },
  { id: "academic", emoji: "🎓", label: "Academic Literature Review", hint: "Rigorous" },
];

export type Session = {
  id: string;
  title: string;
  mode: ResearchMode;
  group: "Today" | "Previous 7 Days" | "Older";
};

export type Citation = {
  id: number;
  title: string;
  url: string;
  publisher: string;
  credibility: number;
  credibilityLabel: string;
  quote: string;
  claim: "FACT" | "FINDING" | "STATISTIC" | "HYPOTHESIS";
  verified: boolean;
  contradiction?: string;
};

export type Plan = {
  objective: string;
  questions: string[];
  hypotheses: { text: string; confidence: number }[];
};

export type Step = { icon: string; label: string; detail: string };

export type AgentCost = { agent: string; tokens: number; cost: number };

export type Metrics = {
  faithfulness: number;
  answerRelevance: number;
  contextPrecision: number;
  agents: AgentCost[];
};

export const SESSIONS: Session[] = [
  { id: "s1", title: "Quantum Error Correction Thresholds", mode: "deep", group: "Today" },
  { id: "s2", title: "LLM Multi-Agent System Security", mode: "academic", group: "Today" },
  { id: "s3", title: "EU AI Act Compliance & Governance", mode: "quick", group: "Previous 7 Days" },
];

export const STEPS: Step[] = [
  {
    icon: "📋",
    label: "Supervisor Formulating Strategy",
    detail: "Decomposing research objective into targeted hypotheses and search queries.",
  },
  {
    icon: "🔍",
    label: "Dual Retrieval (Qdrant RAG + Web)",
    detail: "Querying dense/sparse hybrid vector store and real-time academic sources.",
  },
  {
    icon: "🔬",
    label: "Fact Extraction & EKG Linking",
    detail: "Extracting atomic claims, evaluating credibility C(S), and linking graph edges.",
  },
  {
    icon: "📝",
    label: "Grounded Report Synthesis",
    detail: "Synthesizing publication-grade report with inline numbered citations.",
  },
];

export const PLAN: Plan = {
  objective:
    "Evaluate state-of-the-art architectures for multi-agent reasoning, verification, and defense mechanisms.",
  questions: [
    "What are the primary attack vectors in agentic tool-use loops?",
    "How does dual-LLM verification impact reasoning latency and cost?",
    "What empirical evidence demonstrates improved safety alignment?",
  ],
  hypotheses: [
    { text: "Multi-agent dual verification reduces prompt injection vulnerability by >80%.", confidence: 92 },
    { text: "Dynamic query decomposition improves precision in domain-specific technical queries.", confidence: 88 },
  ],
};

export const REPORT = `# Research Synthesis: Autonomous Multi-Agent Systems & Verification

## Executive Summary
Recent empirical breakthroughs demonstrate that multi-agent collaborative networks significantly outperform single-model prompting across complex multi-step reasoning workflows [1]. However, expanded agent tool-use introduces heightened exposure to indirect prompt injection and cascading hallucination risks [2].

## Key Findings & Empirical Analysis
- **Reasoning Fidelity**: Structured supervisor-worker state machines improve answer consistency on technical queries by **28.4%** compared to naive Zero-Shot chain-of-thought [1].
- **Defense Protocols**: Dual-agent adversarial review gates verify citation grounding against extracted knowledge graph nodes with **96.2% faithfulness** [3].
- **Cost & Latency Trade-offs**: While multi-iteration search loops increase total token consumption by ~2.4x, early convergence algorithms bound latency within acceptable bounds.

## Strategic Implications & Recommendations
1. Implement mandatory human-in-the-loop (HITL) approval gates before executing multi-hop write operations.
2. Utilize dense + sparse hybrid vector indexing (Qdrant RRF) for verified document grounding.

## References
- [1] Nature Intelligence: Multi-Agent Collaboration Benchmarks (2025)
- [2] IEEE Transactions on AI Safety & Security (2025)
- [3] DeepResearch Relational Knowledge Graph Verification Engine (2026)
`;

export const CITATIONS: Citation[] = [
  {
    id: 1,
    title: "Multi-Agent Collaboration Benchmarks in Complex Reasoning",
    url: "https://nature.com/articles/s41586-025-001",
    publisher: "Nature Intelligence",
    credibility: 0.96,
    credibilityLabel: "Academic Peer-Reviewed",
    quote: "Multi-agent networks achieved a 28.4% improvement in reasoning benchmarks over single-prompt models.",
    claim: "FINDING",
    verified: true,
  },
  {
    id: 2,
    title: "Indirect Prompt Injection in Autonomous Tool-Use Environments",
    url: "https://ieee.org/abstract/document/998811",
    publisher: "IEEE Transactions on AI Security",
    credibility: 0.94,
    credibilityLabel: "Peer-Reviewed Security Journal",
    quote: "Expanded tool-use pipelines exhibit vulnerability to indirect prompt injections without isolated parsing.",
    claim: "FACT",
    verified: true,
  },
  {
    id: 3,
    title: "Grounding and Faithfulness Metrics in Relational Evidence Graphs",
    url: "https://arxiv.org/abs/2602.0001",
    publisher: "arXiv Computer Science",
    credibility: 0.91,
    credibilityLabel: "Preprint Archive",
    quote: "Dual-agent verification achieved 96.2% faithfulness against ground truth evidence items.",
    claim: "STATISTIC",
    verified: true,
  },
];

export const METRICS: Metrics = {
  faithfulness: 0.96,
  answerRelevance: 0.94,
  contextPrecision: 0.91,
  agents: [
    { agent: "Supervisor / Planner", tokens: 2300, cost: 0.008 },
    { agent: "Search Agent (RAG + Web)", tokens: 4800, cost: 0.016 },
    { agent: "Fact Extractor", tokens: 3600, cost: 0.012 },
    { agent: "Synthesizer", tokens: 5500, cost: 0.021 },
  ],
};
