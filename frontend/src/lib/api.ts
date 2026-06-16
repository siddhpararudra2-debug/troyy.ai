/**
 * Troy — API Client
 * Type-safe fetch wrapper for communicating with the FastAPI backend.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

interface ApiError {
  detail: string;
  status: number;
}

class TroyApiClient {
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

  // ── Calculations ────────────────────────────────────────────
  async calculate(data: {
    formula_id: string;
    parameters: Record<string, number>;
    project_id?: string;
    unit_system?: string;
  }) {
    return this.request<CalculationResponse>("/calculate", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  // ── Formulas ────────────────────────────────────────────────
  async getFormulas(params?: {
    domain?: string;
    category?: string;
    search?: string;
  }) {
    const searchParams = new URLSearchParams();
    if (params?.domain) searchParams.set("domain", params.domain);
    if (params?.category) searchParams.set("category", params.category);
    if (params?.search) searchParams.set("search", params.search);
    const query = searchParams.toString();
    return this.request<FormulaListResponse>(
      `/formulas${query ? `?${query}` : ""}`
    );
  }

  async getFormula(formulaId: string) {
    return this.request<FormulaResponse>(`/formulas/${formulaId}`);
  }

  // ── Projects ────────────────────────────────────────────────
  async createProject(data: {
    name: string;
    description?: string;
    domain?: string;
  }) {
    return this.request<ProjectResponse>("/projects", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async getProjects() {
    return this.request<ProjectListResponse>("/projects");
  }

  async getProject(id: string) {
    return this.request<ProjectResponse>(`/projects/${id}`);
  }

  // ── Units ───────────────────────────────────────────────────
  async convertUnit(data: {
    value: number;
    from_unit: string;
    to_unit: string;
  }) {
    return this.request<UnitConversionResponse>("/units/convert", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async getUnitSystems() {
    return this.request<{ systems: Record<string, Record<string, string>> }>(
      "/units/systems"
    );
  }

  // ── Memory ──────────────────────────────────────────────────
  async addMemory(data: {
    project_id: string;
    entry_type: string;
    content: string;
    context?: string;
    tags?: string[];
  }) {
    return this.request<MemoryResponse>("/memory", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async getProjectMemory(projectId: string) {
    return this.request<MemoryListResponse>(`/memory/project/${projectId}`);
  }

  // ── Documents ───────────────────────────────────────────────
  async generateDocument(data: {
    project_id: string;
    calculation_id?: string;
    doc_type?: string;
    title?: string;
  }) {
    return this.request<DocumentResponse>("/documents/generate", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async getProjectDocuments(projectId: string) {
    return this.request<DocumentListResponse>(
      `/documents/project/${projectId}`
    );
  }

  // ── Chat ────────────────────────────────────────────────────
  async createChatSession(projectId: string, title?: string) {
    return this.request<ChatSessionResponse>("/chat/sessions", {
      method: "POST",
      body: JSON.stringify({ project_id: projectId, title }),
    });
  }

  async getChatSessions(projectId: string) {
    return this.request<ChatSessionListResponse>(`/chat/sessions/project/${projectId}`);
  }

  async getChatMessages(sessionId: string) {
    return this.request<ChatMessageResponse[]>(`/chat/sessions/${sessionId}/messages`);
  }

  async sendChatMessage(sessionId: string, content: string, metadata?: any) {
    return this.request<ChatMessageResponse>(`/chat/sessions/${sessionId}/messages`, {
      method: "POST",
      body: JSON.stringify({ content, metadata }),
    });
  }

  // ── Health ──────────────────────────────────────────────────
  async healthCheck() {
    return this.request<{
      status: string;
      app: string;
      version: string;
      formulas_loaded: number;
      domains: string[];
    }>("/health".replace("/api/v1", ""));
  }
}

// ── Types ──────────────────────────────────────────────────────
export interface CalculationStep {
  order: number;
  step_type: string;
  description: string;
  latex: string;
  variables: Record<string, string>;
}

export interface ParameterInfo {
  name: string;
  symbol: string;
  unit: string;
  description: string;
  min_value: number | null;
  max_value: number | null;
  default: number | null;
}

export interface OutputInfo {
  name: string;
  symbol: string;
  unit: string;
  description: string;
}

export interface FormulaResponse {
  id: string;
  domain: string;
  category: string;
  name: string;
  description: string;
  formula_latex: string;
  parameters: ParameterInfo[];
  outputs: OutputInfo[];
  reference: string;
  tags: string[];
}

export interface FormulaListResponse {
  formulas: FormulaResponse[];
  total: number;
  domains: string[];
}

export interface CalculationResponse {
  id: string;
  formula_id: string;
  title: string;
  formula: FormulaResponse | null;
  steps: CalculationStep[];
  results: Record<string, number>;
  results_formatted: Record<string, string>;
  latex_summary: string;
  execution_time_ms: number;
  warnings: string[];
  error: string | null;
}

export interface ProjectResponse {
  id: string;
  name: string;
  description: string;
  domain: string;
  status: string;
  created_at: string;
  updated_at: string;
  calculation_count: number;
  document_count: number;
}

export interface ProjectListResponse {
  projects: ProjectResponse[];
  total: number;
}

export interface UnitConversionResponse {
  original_value: number;
  original_unit: string;
  converted_value: number;
  target_unit: string;
  formula: string;
}

export interface MemoryResponse {
  id: string;
  project_id: string;
  entry_type: string;
  content: string;
  context: string;
  tags: string[];
  relevance_score: number;
  created_at: string;
}

export interface MemoryListResponse {
  entries: MemoryResponse[];
  total: number;
}

export interface DocumentResponse {
  id: string;
  project_id: string;
  calculation_id: string | null;
  title: string;
  doc_type: string;
  format: string;
  content: string;
  created_at: string;
}

export interface DocumentListResponse {
  documents: DocumentResponse[];
  total: number;
}

export interface ChatMessageResponse {
  id: string;
  session_id: string;
  role: "user" | "assistant" | "system";
  content: string;
  metadata: any;
  created_at: string;
}

export interface ChatSessionResponse {
  id: string;
  project_id: string;
  title: string;
  created_at: string;
  updated_at: string;
  messages: ChatMessageResponse[];
}

export interface ChatSessionListResponse {
  sessions: ChatSessionResponse[];
  total: number;
}

// ── Singleton Export ────────────────────────────────────────────
export const api = new TroyApiClient();
export default api;
