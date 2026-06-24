"use client";

import { useState, useEffect } from "react";
import { eosApi, HealthResponse, AgentStatusResponse } from "@/lib/api-engineering-os";

type TabType = "chat" | "agents" | "knowledge" | "memory" | "health";

export default function EngineeringOSDashboard() {
  const [activeTab, setActiveTab] = useState<TabType>("health");
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [agentStatus, setAgentStatus] = useState<AgentStatusResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadStatus();
    const interval = setInterval(loadStatus, 15000);
    return () => clearInterval(interval);
  }, []);

  async function loadStatus() {
    try {
      const [h, a] = await Promise.all([
        eosApi.healthCheck(),
        eosApi.getAgentStatus(),
      ]);
      setHealth(h);
      setAgentStatus(a);
    } catch (err) {
      console.error("Failed to load status:", err);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{
      minHeight: "100vh",
      background: "var(--bg-primary)",
      color: "var(--text-primary)",
      fontFamily: "system-ui, -apple-system, sans-serif",
    }}>
      {/* Top Navigation */}
      <header style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        padding: "12px 24px",
        borderBottom: "1px solid var(--border-primary)",
        background: "rgba(10, 14, 23, 0.9)",
        backdropFilter: "blur(12px)",
        position: "sticky",
        top: 0,
        zIndex: 100,
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <div style={{
            width: 32, height: 32,
            borderRadius: 8,
            background: "linear-gradient(135deg, #3b82f6, #8b5cf6)",
            display: "flex", alignItems: "center", justifyContent: "center",
            fontWeight: 800, fontSize: "0.9rem", color: "white",
          }}>E</div>
          <h1 style={{ fontSize: "1rem", fontWeight: 700 }}>Engineering OS</h1>
          <span style={{
            padding: "2px 8px",
            borderRadius: 4,
            fontSize: "0.65rem",
            background: "rgba(59,130,246,0.15)",
            color: "#3b82f6",
            fontWeight: 600,
          }}>Sprint 1</span>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          {health?.status?.ollama_connected ? (
            <span style={{
              display: "flex", alignItems: "center", gap: 4,
              fontSize: "0.75rem", color: "#10b981",
            }}>
              <span style={{ width: 6, height: 6, borderRadius: "50%", background: "#10b981" }} />
              Ollama Online
            </span>
          ) : (
            <span style={{
              display: "flex", alignItems: "center", gap: 4,
              fontSize: "0.75rem", color: "#ef4444",
            }}>
              <span style={{ width: 6, height: 6, borderRadius: "50%", background: "#ef4444" }} />
              Ollama Offline
            </span>
          )}
        </div>
      </header>

      {/* Tab Navigation */}
      <div style={{
        display: "flex",
        gap: 4,
        padding: "12px 24px",
        borderBottom: "1px solid var(--border-secondary)",
        background: "var(--bg-secondary)",
      }}>
        {(["health", "chat", "agents", "knowledge", "memory"] as TabType[]).map(tab => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            style={{
              padding: "8px 16px",
              borderRadius: 8,
              border: "none",
              cursor: "pointer",
              background: activeTab === tab ? "var(--accent-subtle)" : "transparent",
              color: activeTab === tab ? "var(--accent)" : "var(--text-secondary)",
              fontWeight: activeTab === tab ? 600 : 400,
              fontSize: "0.8125rem",
              transition: "all 0.2s",
              textTransform: "capitalize",
            }}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* Main Content */}
      <div style={{ padding: "24px", maxWidth: 1200, margin: "0 auto" }}>
        {activeTab === "health" && <HealthPanel health={health} loading={loading} />}
        {activeTab === "chat" && <ChatPanel />}
        {activeTab === "agents" && <AgentsPanel agentStatus={agentStatus} />}
        {activeTab === "knowledge" && <KnowledgePanel />}
        {activeTab === "memory" && <MemoryPanel />}
      </div>
    </div>
  );
}

function HealthPanel({ health, loading }: { health: HealthResponse | null; loading: boolean }) {
  if (loading) return <div style={{ textAlign: "center", padding: 40 }}>Loading system status...</div>;
  if (!health) return <div style={{ textAlign: "center", padding: 40 }}>Failed to connect to backend</div>;

  return (
    <div>
      <h2 style={{ fontSize: "1.25rem", fontWeight: 700, marginBottom: 20 }}>System Health</h2>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: 16 }}>
        <StatusCard title="Ollama Status" status={health.status.ollama_connected ? "Healthy" : "Offline"}
          color={health.status.ollama_connected ? "#10b981" : "#ef4444"} />
        <StatusCard title="System Status" status={health.status.status}
          color={health.status.status === "healthy" ? "#10b981" : "#f59e0b"} />
        <StatusCard title="Active Sessions" status={`${health.status.active_sessions}`} color="#3b82f6" />
        <StatusCard title="Available Models" status={`${health.status.available_models.length}`} color="#8b5cf6" />
      </div>
      
      {health.status.available_models.length > 0 && (
        <div style={{ marginTop: 24 }}>
          <h3 style={{ fontSize: "1rem", fontWeight: 600, marginBottom: 12 }}>Models</h3>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
            {health.status.available_models.map(model => (
              <span key={model} style={{
                padding: "4px 12px",
                borderRadius: 20,
                background: "rgba(59,130,246,0.1)",
                border: "1px solid rgba(59,130,246,0.2)",
                fontSize: "0.8125rem",
                color: "#60a5fa",
              }}>{model}</span>
            ))}
          </div>
        </div>
      )}

      {Object.keys(health.status.model_health).length > 0 && (
        <div style={{ marginTop: 24 }}>
          <h3 style={{ fontSize: "1rem", fontWeight: 600, marginBottom: 12 }}>Model Performance</h3>
          <div style={{ display: "grid", gap: 8 }}>
            {Object.entries(health.status.model_health).map(([name, stats]) => (
              <div key={name} style={{
                display: "flex", justifyContent: "space-between",
                padding: "12px 16px",
                background: "var(--bg-secondary)",
                borderRadius: 8,
                border: "1px solid var(--border-secondary)",
                fontSize: "0.8125rem",
              }}>
                <span style={{ fontWeight: 600 }}>{name}</span>
                <span style={{ color: "var(--text-secondary)" }}>
                  RT: {stats.avg_response_time.toFixed(2)}s | Reqs: {stats.total_requests} | Errors: {stats.error_count}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      <div style={{ marginTop: 24 }}>
        <h3 style={{ fontSize: "1rem", fontWeight: 600, marginBottom: 12 }}>Components</h3>
        <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
          {Object.entries(health.components).map(([name, status]) => (
            <span key={name} style={{
              padding: "4px 12px",
              borderRadius: 20,
              background: status === "operational" ? "rgba(16,185,129,0.1)" : "rgba(239,68,68,0.1)",
              border: `1px solid ${status === "operational" ? "rgba(16,185,129,0.2)" : "rgba(239,68,68,0.2)"}`,
              fontSize: "0.8125rem",
              color: status === "operational" ? "#10b981" : "#ef4444",
              textTransform: "capitalize",
            }}>
              {name}: {status}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}

function StatusCard({ title, status, color }: { title: string; status: string; color: string }) {
  return (
    <div style={{
      padding: 20,
      background: "var(--bg-secondary)",
      borderRadius: 12,
      border: "1px solid var(--border-secondary)",
    }}>
      <div style={{ fontSize: "0.75rem", color: "var(--text-tertiary)", marginBottom: 8 }}>{title}</div>
      <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
        <span style={{ width: 8, height: 8, borderRadius: "50%", background: color }} />
        <span style={{ fontSize: "1.5rem", fontWeight: 700, color }}>{status}</span>
      </div>
    </div>
  );
}

function ChatPanel() {
  const [messages, setMessages] = useState<{ role: string; content: string }[]>([]);
  const [input, setInput] = useState("");
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [sending, setSending] = useState(false);

  async function sendMessage() {
    if (!input.trim() || sending) return;
    setSending(true);
    setMessages(prev => [...prev, { role: "user", content: input }]);
    
    try {
      const result = await eosApi.chat({
        message: input,
        session_id: sessionId || undefined,
      });
      setSessionId(result.session_id);
      setMessages(prev => [...prev, { role: "assistant", content: result.response }]);
    } catch (err) {
      setMessages(prev => [...prev, { role: "assistant", content: "Error: Failed to get response" }]);
    }
    setInput("");
    setSending(false);
  }

  return (
    <div>
      <h2 style={{ fontSize: "1.25rem", fontWeight: 700, marginBottom: 20 }}>AI Chat</h2>
      <div style={{
        height: 400,
        overflowY: "auto",
        padding: 16,
        background: "var(--bg-secondary)",
        borderRadius: 12,
        border: "1px solid var(--border-secondary)",
        marginBottom: 16,
        display: "flex",
        flexDirection: "column",
        gap: 12,
      }}>
        {messages.length === 0 && (
          <div style={{ textAlign: "center", color: "var(--text-tertiary)", padding: 40 }}>
            Start a conversation with the AI...
          </div>
        )}
        {messages.map((msg, i) => (
          <div key={i} style={{
            alignSelf: msg.role === "user" ? "flex-end" : "flex-start",
            maxWidth: "80%",
            padding: "10px 16px",
            borderRadius: 12,
            background: msg.role === "user" ? "rgba(59,130,246,0.15)" : "rgba(30,41,59,0.5)",
            border: `1px solid ${msg.role === "user" ? "rgba(59,130,246,0.2)" : "rgba(100,116,139,0.2)"}`,
            fontSize: "0.875rem",
            lineHeight: 1.5,
            whiteSpace: "pre-wrap",
          }}>
            <div style={{ fontSize: "0.65rem", color: "var(--text-muted)", marginBottom: 4, textTransform: "uppercase" }}>
              {msg.role}
            </div>
            {msg.content}
          </div>
        ))}
      </div>
      <div style={{ display: "flex", gap: 8 }}>
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === "Enter" && sendMessage()}
          placeholder="Ask an engineering question..."
          style={{
            flex: 1,
            padding: "10px 16px",
            borderRadius: 8,
            border: "1px solid var(--border-primary)",
            background: "var(--bg-secondary)",
            color: "var(--text-primary)",
            fontSize: "0.875rem",
            outline: "none",
          }}
        />
        <button onClick={sendMessage} disabled={sending} style={{
          padding: "10px 20px",
          borderRadius: 8,
          border: "none",
          background: "var(--accent)",
          color: "white",
          fontWeight: 600,
          cursor: "pointer",
          opacity: sending ? 0.6 : 1,
          fontSize: "0.875rem",
        }}>
          {sending ? "..." : "Send"}
        </button>
      </div>
    </div>
  );
}

function AgentsPanel({ agentStatus }: { agentStatus: AgentStatusResponse | null }) {
  return (
    <div>
      <h2 style={{ fontSize: "1.25rem", fontWeight: 700, marginBottom: 20 }}>Engineering Agents</h2>
      
      {agentStatus && (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: 16, marginBottom: 24 }}>
          <StatusCard title="Total Tasks" status={`${agentStatus.tasks.total_tasks}`} color="#3b82f6" />
          <StatusCard title="Completed" status={`${agentStatus.tasks.completed}`} color="#10b981" />
          <StatusCard title="Running" status={`${agentStatus.tasks.running}`} color="#f59e0b" />
          <StatusCard title="Success Rate" status={`${agentStatus.tasks.success_rate.toFixed(0)}%`} color="#8b5cf6" />
        </div>
      )}

      {agentStatus?.agent_types.map(type => (
        <div key={type} style={{
          padding: 16,
          background: "var(--bg-secondary)",
          borderRadius: 12,
          border: "1px solid var(--border-secondary)",
          marginBottom: 12,
        }}>
          <div style={{ fontSize: "0.9375rem", fontWeight: 700, marginBottom: 8, textTransform: "capitalize" }}>
            {type} Agent
          </div>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 4 }}>
            {(agentStatus.capabilities[type] || []).map(cap => (
              <span key={cap} style={{
                padding: "2px 8px",
                borderRadius: 4,
                background: "rgba(16,185,129,0.1)",
                fontSize: "0.75rem",
                color: "#10b981",
              }}>{cap}</span>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

function KnowledgePanel() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<any[]>([]);
  const [searching, setSearching] = useState(false);

  async function search() {
    if (!query.trim()) return;
    setSearching(true);
    try {
      const res = await eosApi.searchKnowledge({ query, limit: 10 });
      setResults(res.results);
    } catch (err) {
      console.error(err);
    }
    setSearching(false);
  }

  return (
    <div>
      <h2 style={{ fontSize: "1.25rem", fontWeight: 700, marginBottom: 20 }}>Knowledge Base</h2>
      <div style={{ display: "flex", gap: 8, marginBottom: 20 }}>
        <input
          value={query}
          onChange={e => setQuery(e.target.value)}
          onKeyDown={e => e.key === "Enter" && search()}
          placeholder="Search engineering knowledge..."
          style={{
            flex: 1,
            padding: "10px 16px",
            borderRadius: 8,
            border: "1px solid var(--border-primary)",
            background: "var(--bg-secondary)",
            color: "var(--text-primary)",
            fontSize: "0.875rem",
            outline: "none",
          }}
        />
        <button onClick={search} disabled={searching} style={{
          padding: "10px 20px",
          borderRadius: 8,
          border: "none",
          background: "var(--accent)",
          color: "white",
          fontWeight: 600,
          cursor: "pointer",
          fontSize: "0.875rem",
        }}>
          {searching ? "..." : "Search"}
        </button>
      </div>

      <div style={{ display: "grid", gap: 8 }}>
        {results.map((r, i) => (
          <div key={i} style={{
            padding: 16,
            background: "var(--bg-secondary)",
            borderRadius: 8,
            border: "1px solid var(--border-secondary)",
          }}>
            <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 8 }}>
              <span style={{ fontSize: "0.8125rem", fontWeight: 600 }}>{r.title || "Untitled"}</span>
              <span style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>
                Score: {r.score.toFixed(3)}
              </span>
            </div>
            <p style={{ fontSize: "0.8125rem", color: "var(--text-secondary)", lineHeight: 1.5 }}>
              {r.content.slice(0, 200)}...
            </p>
            {r.source && (
              <div style={{ fontSize: "0.7rem", color: "var(--text-muted)", marginTop: 8 }}>
                Source: {r.source}
              </div>
            )}
          </div>
        ))}
        {query && !searching && results.length === 0 && (
          <div style={{ textAlign: "center", padding: 40, color: "var(--text-tertiary)" }}>
            No results found. Check that knowledge base has been indexed.
          </div>
        )}
      </div>
    </div>
  );
}

function MemoryPanel() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<any[]>([]);
  const [searching, setSearching] = useState(false);

  async function search() {
    if (!query.trim()) return;
    setSearching(true);
    try {
      const res = await eosApi.searchMemory({ query, limit: 20 });
      setResults(res.results);
    } catch (err) {
      console.error(err);
    }
    setSearching(false);
  }

  return (
    <div>
      <h2 style={{ fontSize: "1.25rem", fontWeight: 700, marginBottom: 20 }}>Project Memory</h2>
      <div style={{ display: "flex", gap: 8, marginBottom: 20 }}>
        <input
          value={query}
          onChange={e => setQuery(e.target.value)}
          onKeyDown={e => e.key === "Enter" && search()}
          placeholder="Search project memory..."
          style={{
            flex: 1,
            padding: "10px 16px",
            borderRadius: 8,
            border: "1px solid var(--border-primary)",
            background: "var(--bg-secondary)",
            color: "var(--text-primary)",
            fontSize: "0.875rem",
            outline: "none",
          }}
        />
        <button onClick={search} disabled={searching} style={{
          padding: "10px 20px",
          borderRadius: 8,
          border: "none",
          background: "var(--accent)",
          color: "white",
          fontWeight: 600,
          cursor: "pointer",
          fontSize: "0.875rem",
        }}>
          {searching ? "..." : "Search"}
        </button>
      </div>

      <div style={{ display: "grid", gap: 8 }}>
        {results.map((r, i) => (
          <div key={i} style={{
            padding: 16,
            background: "var(--bg-secondary)",
            borderRadius: 8,
            border: "1px solid var(--border-secondary)",
          }}>
            <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 8 }}>
              <div>
                <span style={{
                  padding: "2px 8px",
                  borderRadius: 4,
                  background: "rgba(99,102,241,0.1)",
                  fontSize: "0.7rem",
                  color: "#818cf8",
                  fontWeight: 600,
                  textTransform: "uppercase",
                }}>{r.memory_type}</span>
                {r.title && (
                  <span style={{ fontSize: "0.8125rem", fontWeight: 600, marginLeft: 8 }}>{r.title}</span>
                )}
              </div>
              <span style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>
                Score: {r.score.toFixed(2)}
              </span>
            </div>
            <p style={{ fontSize: "0.8125rem", color: "var(--text-secondary)", lineHeight: 1.5 }}>
              {r.content.slice(0, 250)}...
            </p>
          </div>
        ))}
        {query && !searching && results.length === 0 && (
          <div style={{ textAlign: "center", padding: 40, color: "var(--text-tertiary)" }}>
            No memories found for this query.
          </div>
        )}
      </div>
    </div>
  );
}