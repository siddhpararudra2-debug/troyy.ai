/**
 * Engineering OS - API Client
 * Type-safe fetch wrapper for Engineering OS Sprint 1 API.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

interface ApiError {
  detail: string;
  status: number;
}

export class EngineeringOSClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const config: RequestInit = {
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
      ...options,
    };

    const response = await fetch(url, config);

    if (!response.ok) {
      const error: ApiError = {
        detail: await response.text(),
        status: response.status,
      };
      throw error;
    }

    if (response.status === 204) {
      return undefined as T;
    }

    return response.json();
  }

  // ── Chat ────────────────────────────────────────────────────
  async chat(data: {
    message: string;
    session_id?: string;
    project_id?: string;
    task_type?: string;
    stream?: boolean;
    temperature?: number;
  }) {
    return this.request<ChatResponse>("/chat", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  // ── Projects ────────────────────────────────────────────────
  async createProject(data: {
    name: string;
    description?: string;
    tags?: string[];
  }) {
    return this.request<ProjectResponse>("/projects", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async getProject(id: string) {
    return this.request<ProjectResponse>(`/projects/${id}`);
  }

  // ── Memory ──────────────────────────────────────────────────
  async storeMemory(data: {
    project_id: string;
    memory_type: string;
    content: string;
    title?: string;
    summary?: string;
    importance?: number;
    tags?: string[];
  }) {
    return this.request<MemoryResponse>("/memory/store", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async searchMemory(data: {
    query: string;
    project_id?: string;
    memory_types?: string[];
    limit?: number;
  }) {
    return this.request<MemorySearchResponse>("/memory/search", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  // ── Knowledge ───────────────────────────────────────────────
  async searchKnowledge(data: {
    query: string;
    collection?: string;
    limit?: number;
    score_threshold?: number;
  }) {
    return this.request<KnowledgeSearchResponse>("/knowledge/search", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  // ── Agents ──────────────────────────────────────────────────
  async executeAgent(data: {
    project_id: string;
    agent_type: string;
    title: string;
    description: string;
    input_data?: Record<string, unknown>;
    priority?: number;
  }) {
    return this.request<AgentExecuteResponse>("/agents/execute", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async getAgentStatus() {
    return this.request<AgentStatusResponse>("/agents/status");
  }

  // ── Health ──────────────────────────────────────────────────
  async healthCheck() {
    return this.request<HealthResponse>("/health");
  }
}

// ── Types ──────────────────────────────────────────────────────
export interface ChatResponse {
  response: string;
  session_id: string;
  model_used: string;
  task_type: string;
  response_time: number;
}

export interface ProjectResponse {
  id: string;
  name: string;
  description?: string;
  status: string;
  tags: string[];
  created_at: string;
}

export interface MemoryResponse {
  id: string;
  project_id: string;
  memory_type: string;
  title?: string;
  summary?: string;
  importance: number;
  created_at: string;
}

export interface MemorySearchResult {
  content: string;
  memory_type: string;
  title?: string;
  summary?: string;
  source?: string;
  importance: number;
  score: number;
}

export interface MemorySearchResponse {
  results: MemorySearchResult[];
}

export interface KnowledgeSearchResult {
  id: string;
  score: number;
  content: string;
  title?: string;
  source?: string;
  chunk_index?: number;
  asset_type?: string;
}

export interface KnowledgeSearchResponse {
  results: KnowledgeSearchResult[];
}

export interface AgentExecuteResponse {
  task_id: string;
  status: string;
}

export interface AgentStatusResponse {
  running: boolean;
  agents: number;
  agent_types: string[];
  capabilities: Record<string, string[]>;
  tasks: {
    total_tasks: number;
    completed: number;
    failed: number;
    running: number;
    pending: number;
    success_rate: number;
  };
}

export interface HealthResponse {
  system: string;
  version: string;
  status: {
    status: string;
    ollama_connected: boolean;
    available_models: string[];
    active_sessions: number;
    model_health: Record<string, {
      available: boolean;
      avg_response_time: number;
      total_requests: number;
      error_count: number;
    }>;
  };
  components: Record<string, string>;
}

export const eosApi = new EngineeringOSClient();
export default eosApi;