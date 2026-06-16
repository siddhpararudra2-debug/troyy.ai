"use client";

import { useState, useRef, useEffect } from "react";
import { api, ChatMessageResponse, ChatSessionResponse } from "@/lib/api";

export default function ChatInterface() {
  const [session, setSession] = useState<ChatSessionResponse | null>(null);
  const [messages, setMessages] = useState<ChatMessageResponse[]>([]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  useEffect(() => {
    initSession();
  }, []);

  async function initSession() {
    try {
      // Create or get a session for the default project
      const projectId = "default";
      const sessionList = await api.getChatSessions(projectId);
      
      let currentSession;
      if (sessionList.sessions.length > 0) {
        currentSession = sessionList.sessions[0];
      } else {
        currentSession = await api.createChatSession(projectId, "Dashboard Chat");
      }
      
      setSession(currentSession);
      
      // Load messages
      const msgs = await api.getChatMessages(currentSession.id);
      
      if (msgs.length === 0) {
        // Add a local welcome message
        setMessages([{
          id: "welcome",
          session_id: currentSession.id,
          role: "assistant",
          content: "Troy Engineering Copilot initialized. I have full access to this project's memory, calculations, and documents. What are we analyzing today?",
          metadata: {},
          created_at: new Date().toISOString()
        }]);
      } else {
        setMessages(msgs);
      }
    } catch (e) {
      console.error("Failed to initialize chat session", e);
    }
  }

  const handleSend = async () => {
    if (!input.trim() || !session) return;

    const userText = input;
    setInput("");
    
    // Optimistic UI update
    const optimisticMsg: ChatMessageResponse = {
      id: "temp-" + Date.now(),
      session_id: session.id,
      role: "user",
      content: userText,
      metadata: {},
      created_at: new Date().toISOString()
    };
    
    setMessages((prev) => [...prev, optimisticMsg]);
    setIsTyping(true);

    try {
      // Send to backend
      const aiResponse = await api.sendChatMessage(session.id, userText);
      
      // Replace optimistic message and add AI response by fetching all
      const msgs = await api.getChatMessages(session.id);
      setMessages(msgs);
    } catch (e) {
      console.error("Failed to send message", e);
      // fallback error message
      setMessages((prev) => [...prev, {
        id: "error-" + Date.now(),
        session_id: session.id,
        role: "assistant",
        content: "⚠️ I encountered an error connecting to the Context Engine.",
        metadata: {},
        created_at: new Date().toISOString()
      }]);
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%", background: "var(--bg-card)", borderRight: "1px solid var(--border-primary)" }}>
      {/* Header */}
      <div style={{ padding: "var(--space-md)", borderBottom: "1px solid var(--border-primary)", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <h2 style={{ fontSize: "1rem", fontWeight: 700, display: "flex", alignItems: "center", gap: "var(--space-sm)" }}>
          <span style={{ fontSize: "1.2rem" }}>🧠</span> Copilot Chat
        </h2>
        <div style={{ display: "flex", gap: "var(--space-xs)" }}>
            <span className={`badge ${session ? 'badge-aerospace' : 'badge-robotics'}`}>
              {session ? 'Memory Sync Active' : 'Connecting...'}
            </span>
        </div>
      </div>

      {/* Messages */}
      <div style={{ flex: 1, overflowY: "auto", padding: "var(--space-md)", display: "flex", flexDirection: "column", gap: "var(--space-md)" }}>
        {messages.map((msg) => (
          <div
            key={msg.id}
            style={{
              alignSelf: msg.role === "user" ? "flex-end" : "flex-start",
              maxWidth: "85%",
              background: msg.role === "user" ? "var(--bg-tertiary)" : "rgba(59, 130, 246, 0.1)",
              border: `1px solid ${msg.role === "user" ? "var(--border-secondary)" : "rgba(59, 130, 246, 0.2)"}`,
              padding: "var(--space-sm) var(--space-md)",
              borderRadius: "var(--radius-lg)",
              borderBottomRightRadius: msg.role === "user" ? 0 : "var(--radius-lg)",
              borderTopLeftRadius: msg.role === "assistant" || msg.role === "system" ? 0 : "var(--radius-lg)",
            }}
          >
            <div style={{ fontSize: "0.6875rem", color: "var(--text-muted)", marginBottom: 4, fontWeight: 600 }}>
              {msg.role === "user" ? "You" : "Troy AI"}
            </div>
            <div style={{ fontSize: "0.875rem", lineHeight: 1.5, color: "var(--text-primary)", whiteSpace: "pre-wrap" }}>
              {msg.content}
            </div>
          </div>
        ))}
        {isTyping && (
          <div style={{ alignSelf: "flex-start", padding: "var(--space-sm) var(--space-md)", color: "var(--text-muted)", fontSize: "0.8125rem", fontStyle: "italic" }}>
            Processing project context...
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div style={{ padding: "var(--space-md)", borderTop: "1px solid var(--border-primary)" }}>
        <div style={{ display: "flex", gap: "var(--space-sm)" }}>
          <input
            className="input"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                handleSend();
              }
            }}
            placeholder="Ask about formulas, design review, or calculations..."
            style={{ flex: 1, background: "var(--bg-tertiary)", border: "1px solid var(--border-secondary)" }}
            disabled={!session || isTyping}
          />
          <button 
            className="btn btn-primary" 
            onClick={handleSend} 
            disabled={!session || isTyping}
            style={{ padding: "10px 16px", opacity: (!session || isTyping) ? 0.7 : 1 }}
          >
            Send
          </button>
        </div>
        <div style={{ fontSize: "0.6875rem", color: "var(--text-muted)", marginTop: 8, textAlign: "center" }}>
          Press Enter to send. The AI automatically queries your recent calculations and constraints.
        </div>
      </div>
    </div>
  );
}
