# DeepResearch – Multi-Agent Ai Research Platform

DeepResearch is a production-grade, enterprise-ready multi-agent AI research platform designed to automate deep, multi-source literature reviews, Web + Document Retrieval Augmented Generation (RAG), relational knowledge graph synthesis, and citation-backed report generation.

exports the following monorepo structure:

## Local Development Setup

### Prerequisites
- Docker & Docker Compose
- Python 3.11+
- Node.js 20+

3## Running via Docker Compose
```bash
# 1. Clone environment settings
cp .env.example .env

# 2. Launch all microservices and infrastructure
docker compose up --build
```

- Frontend: bhttp://localhost:3000`]
- Backend API Docs: bhttp://localhost:8000/api/v1/docs`]
- Backend Health Endpoint: bhttp://localhost:8000/healthzz]
- Backend Readiness Endpoint: bhttp://localhost:8000/readyzz]
