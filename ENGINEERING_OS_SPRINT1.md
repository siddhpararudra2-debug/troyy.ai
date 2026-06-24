# Engineering OS — Sprint 1

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Engineering OS                            │
├─────────────────────────────────────────────────────────────┤
│  Frontend (Next.js + React + TypeScript + Tailwind)         │
│  ┌─────────┬──────────┬──────────┬──────────┬──────────┐   │
│  │Dashboard│   Chat   │ Knowledge│  Memory  │  Agents  │   │
│  └────┬────┴────┬─────┴────┬─────┴────┬─────┴────┬─────┘   │
│       │         │          │          │          │          │
├───────┴─────────┴──────────┴──────────┴──────────┴─────────┤
│  API Layer (FastAPI + Pydantic)                             │
│  ┌─────────┬──────────┬──────────┬──────────┬──────────┐   │
│  │ /chat   │/projects │ /memory  │/knowledge│ /agents  │   │
│  └────┬────┴────┬─────┴────┬─────┴────┬─────┴────┬─────┘   │
├───────┴─────────┴──────────┴──────────┴──────────┴─────────┤
│  Services Layer                                              │
│  ┌──────────┐ ┌─────────┐ ┌─────────┐ ┌───────────────┐   │
│  │  Model   │ │ Memory  │ │   RAG   │ │   Multi-Agent │   │
│  │Orchestrat│ │ System  │ │ Pipeline│ │   Framework   │   │
│  │Qwen Coder│ │Storage  │ │ Qdrant  │ │Mechanical     │   │
│  │DeepSeek  │ │Retrieval│ │Embedding│ │Electronics    │   │
│  │Qwen      │ │Search   │ │Citation │ │PCB,Firmware   │   │
│  └──────────┘ └─────────┘ └─────────┘ │Sim,Doc        │   │
│                                        └───────────────┘   │
├─────────────────────────────────────────────────────────────┤
│  Infrastructure                                              │
│  PostgreSQL │ Redis │ Qdrant │ Ollama │ Celery              │
└─────────────────────────────────────────────────────────────┘
```

## Components

### 1. Local AI Infrastructure (`models/`)
- **OllamaService**: Communicates with local Ollama instance for model inference
- **RoutingService**: Routes tasks to appropriate models (Coding→Qwen Coder, Engineering→DeepSeek-R1, General→Qwen)
- **HealthService**: Monitors model availability, response times, error rates
- **ModelOrchestrator**: Central coordinator managing sessions, inference, and health

### 2. Engineering Workspace (Frontend)
- **Dashboard**: System health overview with real-time status
- **Chat Interface**: AI conversations with session management
- **Knowledge Browser**: Semantic search across engineering knowledge
- **Agent Feed**: Monitor agent task execution
- **Memory Panel**: Browse and search project memory

### 3. Project Memory System (`memory/`)
- **MemoryStorage**: PostgreSQL CRUD for memory entries
- **MemoryRetrieval**: Relevance-scored memory retrieval with context assembly
- **MemoryService**: Unified interface for storing/searching project memories

### 4. Engineering Knowledge System (`rag/`)
- **DocumentIngestor**: PDF/text/markdown ingestion with chunking
- **EmbeddingService**: Local embedding generation via Ollama
- **VectorStore**: Qdrant-based vector storage and semantic search
- **RetrievalService**: Coordinated embedding+search pipeline
- **CitationService**: Source citation generation

### 5. Multi-Agent Framework (`agents/`)
- **BaseAgent**: Abstract agent with LLM integration
- **AgentRegistry**: Agent discovery and capability lookup
- **CommunicationBus**: Publish/subscribe inter-agent messaging
- **TaskManager**: Task lifecycle management
- **AgentRuntime**: Async agent execution environment
- **Specialized Agents**: Mechanical, Electronics, PCB, Firmware, Simulation, Documentation

### Database (`database/`)
11 SQLAlchemy models: User, Project, Conversation, Message, MemoryEntry, EngineeringDecision, Calculation, Document, KnowledgeAsset, AgentTask, AgentExecution
- UUID primary keys, audit fields, soft deletes, comprehensive indexes

### API (`api/routes.py`)
9 endpoints with Pydantic validation and OpenAPI docs:
- `POST /api/v1/chat` - AI chat with model routing
- `POST /api/v1/projects` - Create engineering project
- `GET /api/v1/projects/{id}` - Get project details
- `POST /api/v1/memory/store` - Store memory entry
- `POST /api/v1/memory/search` - Semantic memory search
- `POST /api/v1/knowledge/search` - Knowledge base search
- `POST /api/v1/agents/execute` - Execute agent task
- `GET /api/v1/agents/status` - Agent system status
- `GET /api/v1/health` - System health check

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Ollama with models: `ollama pull qwen`, `ollama pull deepseek-r1`, `ollama pull qwen-coder`

### Launch Full Stack
```bash
docker-compose up -d
```

### Development (without Docker)
```bash
# Backend
pip install -r requirements_sprint1.txt
uvicorn backend.app.main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev
```

### Access
- Frontend: http://localhost:3000/dashboard
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Qdrant Dashboard: http://localhost:6333

## File Structure
```
models/          - Local AI Infrastructure (5 files)
memory/          - Project Memory System (3 files)
rag/             - Engineering Knowledge System (5 files)
agents/          - Multi-Agent Framework (6 files)
api/             - FastAPI Routes (1 file + __init__)
database/        - SQLAlchemy Models + Session (2 files)
backend/app/     - Main entry point + config (3 files)
tests/           - Unit tests (2 files)
frontend/src/    - Next.js frontend components
```

## Testing
```bash
pytest tests/ -v