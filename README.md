# DeepResearch - Multi-Agent AI Research Platform

DeepResearch is an enterprise-grade, citation-backed, multi-agent AI research workspace designed for autonomous, long-running literature reviews, synthesis, and Evidence-driven report generation.

## Architectural Highlights
- **Multi-Agent Workspace**: Orchestrates Supervisor, Planner, Retrieval, Tool, Evidence Collector, Contradiction Checker, Critic, Report Generator, and Citation Verifier agents.
- **Canonical Evidence Model**: All agents communicate through strongly-typed EvidenceItem objects, stored in PostgreSQL (Relational EKG).
- **LiteLLM Gateway**: Unified abstraction for multiple LLM providers, fallback routing, and token cost tracking.
- **Mandatory Research Planning**: Planner agent generates a structured research plan with HITL` approval gates before execution.
- **Production Authentication**: Argon2id password hashing, JWT access tokens, and HTTP-only refresh cookies.

3## Project Structure

```txt
DeepResearch/
‚êò‚êÄ<- docker/compose.infrastructure
 ¿ó‚êÄ backend/                              # FastAPI, SQLAlchemy, Alembic, PYJWT, Passlib
 ‚êò‚êÄ frontend/                             # Next.js 14, Tailwind CSS, Zustand
 ¿ó‚êÄ docker-compose.yml                     # PostgresQL, Redis, Qdrant, Backend, Frotend
``p

## Quick Start

# 1. Clone the Repository
git clone https://github.com/Aniketkoppaka/DeepResearch-Multi-Agent-Research-System.git
cd DeepResearch-Multi-Agent-Research-System

# 2. Start with Docker Compose
docker compose up --build

# 3. Access Services
- Frontend; http://localhost:3000
- Backend API: http://localhost:8000/api/v1
-  API Docs: http://localhost:8000/docs

## License

MIT License ¬© 2026 Aniket Koppaka.
