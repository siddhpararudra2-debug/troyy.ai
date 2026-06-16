"use client";

export default function DocsPage() {
  return (
    <div className="animate-fade-in" style={{ padding: "var(--space-xl)" }}>
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: "var(--space-md)",
          marginBottom: "var(--space-xl)",
        }}
      >
        <span style={{ fontSize: "2rem" }}>📄</span>
        <div>
          <h1 style={{ fontSize: "1.5rem", fontWeight: 800 }}>Documents</h1>
          <p style={{ fontSize: "0.8125rem", color: "var(--text-tertiary)" }}>
            Auto-generated engineering reports
          </p>
        </div>
      </div>

      <div
        className="glass-card"
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          padding: "var(--space-3xl)",
          textAlign: "center",
        }}
      >
        <span style={{ fontSize: "3rem", marginBottom: "var(--space-lg)", opacity: 0.3 }}>
          📄
        </span>
        <h3
          style={{
            fontSize: "1.125rem",
            fontWeight: 700,
            marginBottom: "var(--space-sm)",
          }}
        >
          Documentation Engine
        </h3>
        <p
          style={{
            fontSize: "0.875rem",
            color: "var(--text-tertiary)",
            maxWidth: 400,
            lineHeight: 1.6,
          }}
        >
          Documents are automatically generated when you run calculations.
          Each report includes the full symbolic → numerical → result trace
          with LaTeX-rendered equations.
        </p>
        <p
          style={{
            fontSize: "0.75rem",
            color: "var(--text-muted)",
            marginTop: "var(--space-lg)",
            fontFamily: "var(--font-mono)",
          }}
        >
          Run a calculation to generate your first document →
        </p>
      </div>
    </div>
  );
}
