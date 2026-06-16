"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { api, FormulaResponse } from "@/lib/api";

/* ── Domain Configuration ─────────────────────────────────────── */
const DOMAINS = [
  {
    id: "aerospace",
    name: "Aerospace",
    icon: "✈️",
    description: "Aerodynamics, propulsion, orbital mechanics, structural analysis",
    color: "var(--accent-aerospace)",
    badgeClass: "badge-aerospace",
    stats: { label: "Formulas", count: 0 },
  },
  {
    id: "drones",
    name: "Drones & UAV",
    icon: "🚁",
    description: "Flight dynamics, motor sizing, battery analysis, PID tuning",
    color: "var(--accent-drones)",
    badgeClass: "badge-drones",
    stats: { label: "Formulas", count: 0 },
  },
  {
    id: "robotics",
    name: "Robotics",
    icon: "🤖",
    description: "Kinematics, dynamics, control systems, path planning",
    color: "var(--accent-robotics)",
    badgeClass: "badge-robotics",
    stats: { label: "Formulas", count: 0 },
  },
  {
    id: "electronics",
    name: "Electronics",
    icon: "⚡",
    description: "Circuit analysis, power systems, signal processing, PCB design",
    color: "var(--accent-electronics)",
    badgeClass: "badge-electronics",
    stats: { label: "Formulas", count: 0 },
  },
];

/* ── Main Dashboard ───────────────────────────────────────────── */
export default function Dashboard() {
  const [formulas, setFormulas] = useState<FormulaResponse[]>([]);
  const [domainCounts, setDomainCounts] = useState<Record<string, number>>({});
  const [isLoading, setIsLoading] = useState(true);
  const [backendOnline, setBackendOnline] = useState(false);

  useEffect(() => {
    loadFormulas();
  }, []);

  async function loadFormulas() {
    try {
      const data = await api.getFormulas();
      setFormulas(data.formulas);
      setBackendOnline(true);

      // Count formulas per domain
      const counts: Record<string, number> = {};
      data.formulas.forEach((f) => {
        counts[f.domain] = (counts[f.domain] || 0) + 1;
      });
      setDomainCounts(counts);
    } catch {
      setBackendOnline(false);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div style={{ position: "relative", zIndex: 1, minHeight: "100vh" }}>
      {/* ── Top Bar ─────────────────────────────────────────── */}
      <header
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          padding: "0 var(--space-xl)",
          height: "var(--topbar-height)",
          borderBottom: "1px solid var(--border-primary)",
          background: "rgba(10, 14, 23, 0.8)",
          backdropFilter: "blur(12px)",
          position: "sticky",
          top: 0,
          zIndex: 100,
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "var(--space-md)" }}>
          <div
            style={{
              width: 36,
              height: 36,
              borderRadius: "var(--radius-md)",
              background: "linear-gradient(135deg, var(--accent), #8b5cf6)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: "1.1rem",
              fontWeight: 800,
              color: "white",
            }}
          >
            T
          </div>
          <div>
            <h1
              style={{
                fontSize: "1.125rem",
                fontWeight: 700,
                letterSpacing: "-0.02em",
                lineHeight: 1.2,
              }}
            >
              Troy
            </h1>
            <p
              style={{
                fontSize: "0.6875rem",
                color: "var(--text-tertiary)",
                lineHeight: 1,
                letterSpacing: "0.04em",
                textTransform: "uppercase",
              }}
            >
              Engineering Copilot
            </p>
          </div>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: "var(--space-md)" }}>
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "var(--space-xs)",
              padding: "4px 12px",
              borderRadius: "var(--radius-full)",
              background: backendOnline
                ? "rgba(16, 185, 129, 0.1)"
                : "rgba(239, 68, 68, 0.1)",
              border: `1px solid ${backendOnline ? "rgba(16, 185, 129, 0.2)" : "rgba(239, 68, 68, 0.2)"}`,
            }}
          >
            <div
              style={{
                width: 6,
                height: 6,
                borderRadius: "50%",
                background: backendOnline ? "var(--success)" : "var(--error)",
                boxShadow: backendOnline
                  ? "0 0 8px rgba(16, 185, 129, 0.5)"
                  : "0 0 8px rgba(239, 68, 68, 0.5)",
              }}
            />
            <span
              style={{
                fontSize: "0.6875rem",
                fontWeight: 600,
                color: backendOnline ? "var(--success)" : "var(--error)",
              }}
            >
              {backendOnline ? "Engine Online" : "Engine Offline"}
            </span>
          </div>
          <span
            style={{
              fontSize: "0.6875rem",
              color: "var(--text-muted)",
              fontFamily: "var(--font-mono)",
            }}
          >
            v0.1.0
          </span>
        </div>
      </header>

      {/* ── Hero Section ────────────────────────────────────── */}
      <section
        style={{
          padding: "var(--space-3xl) var(--space-xl) var(--space-2xl)",
          textAlign: "center",
          maxWidth: "800px",
          margin: "0 auto",
        }}
        className="animate-fade-in"
      >
        <div
          style={{
            display: "inline-flex",
            alignItems: "center",
            gap: "var(--space-sm)",
            padding: "6px 16px",
            borderRadius: "var(--radius-full)",
            background: "var(--accent-subtle)",
            border: "1px solid rgba(59, 130, 246, 0.15)",
            marginBottom: "var(--space-lg)",
            fontSize: "0.8125rem",
            color: "var(--accent)",
            fontWeight: 500,
          }}
        >
          <span>🔬</span> Personal Engineering Workbench
        </div>
        <h1
          style={{
            fontSize: "clamp(2rem, 5vw, 3.25rem)",
            fontWeight: 900,
            lineHeight: 1.1,
            letterSpacing: "-0.03em",
            marginBottom: "var(--space-lg)",
            background: "linear-gradient(135deg, var(--text-primary) 0%, var(--accent) 50%, #8b5cf6 100%)",
            backgroundClip: "text",
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent",
            backgroundSize: "200% 200%",
            animation: "gradient-shift 6s ease infinite",
          }}
        >
          Engineering calculations.
          <br />
          Transparent. Precise. Fast.
        </h1>
        <p
          style={{
            fontSize: "1.0625rem",
            color: "var(--text-secondary)",
            maxWidth: "600px",
            margin: "0 auto",
            lineHeight: 1.7,
          }}
        >
          Step-by-step symbolic math, automatic documentation, and project
          memory — every formula shown from first principles, never a black box.
        </p>
      </section>

      {/* ── Domain Cards ────────────────────────────────────── */}
      <section
        style={{
          padding: "0 var(--space-xl) var(--space-3xl)",
          maxWidth: "var(--content-max-width)",
          margin: "0 auto",
        }}
      >
        <div className="grid-4">
          {DOMAINS.map((domain, i) => (
            <Link
              key={domain.id}
              href={`/${domain.id}`}
              style={{ textDecoration: "none", color: "inherit" }}
            >
              <div
                className={`glass-card domain-card ${domain.id}`}
                style={{
                  animationDelay: `${i * 100}ms`,
                  animation: `fadeIn 0.5s ease-out ${i * 100}ms both`,
                }}
              >
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                    marginBottom: "var(--space-md)",
                  }}
                >
                  <span style={{ fontSize: "2rem" }}>{domain.icon}</span>
                  <span className={`badge ${domain.badgeClass}`}>
                    {domainCounts[domain.id] || 0} formulas
                  </span>
                </div>
                <h3
                  style={{
                    fontSize: "1.125rem",
                    fontWeight: 700,
                    marginBottom: "var(--space-sm)",
                  }}
                >
                  {domain.name}
                </h3>
                <p
                  style={{
                    fontSize: "0.8125rem",
                    color: "var(--text-tertiary)",
                    lineHeight: 1.5,
                  }}
                >
                  {domain.description}
                </p>
                <div
                  style={{
                    marginTop: "var(--space-lg)",
                    display: "flex",
                    alignItems: "center",
                    gap: "var(--space-xs)",
                    fontSize: "0.8125rem",
                    fontWeight: 600,
                    color: domain.color,
                  }}
                >
                  Open workspace →
                </div>
              </div>
            </Link>
          ))}
        </div>
      </section>

      {/* ── Formula Explorer ────────────────────────────────── */}
      {formulas.length > 0 && (
        <section
          style={{
            padding: "0 var(--space-xl) var(--space-3xl)",
            maxWidth: "var(--content-max-width)",
            margin: "0 auto",
          }}
        >
          <h2
            style={{
              fontSize: "1.5rem",
              fontWeight: 700,
              marginBottom: "var(--space-lg)",
              display: "flex",
              alignItems: "center",
              gap: "var(--space-sm)",
            }}
          >
            <span
              style={{
                width: 4,
                height: 24,
                borderRadius: 2,
                background: "var(--accent)",
              }}
            />
            Formula Library
            <span
              style={{
                fontSize: "0.875rem",
                fontWeight: 500,
                color: "var(--text-tertiary)",
              }}
            >
              ({formulas.length} available)
            </span>
          </h2>

          <div className="grid-3">
            {formulas.map((formula, i) => (
              <Link
                key={formula.id}
                href={`/${formula.domain}?formula=${formula.id}`}
                style={{ textDecoration: "none", color: "inherit" }}
              >
                <div
                  className="glass-card"
                  style={{
                    animation: `fadeIn 0.4s ease-out ${i * 50}ms both`,
                    height: "100%",
                    display: "flex",
                    flexDirection: "column",
                  }}
                >
                  <div
                    style={{
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "space-between",
                      marginBottom: "var(--space-sm)",
                    }}
                  >
                    <span
                      className={`badge badge-${formula.domain}`}
                    >
                      {formula.domain}
                    </span>
                    <span
                      style={{
                        fontSize: "0.6875rem",
                        color: "var(--text-muted)",
                        fontFamily: "var(--font-mono)",
                      }}
                    >
                      {formula.parameters.length} params
                    </span>
                  </div>
                  <h4
                    style={{
                      fontSize: "0.9375rem",
                      fontWeight: 700,
                      marginBottom: "var(--space-xs)",
                    }}
                  >
                    {formula.name}
                  </h4>
                  <p
                    style={{
                      fontSize: "0.75rem",
                      color: "var(--text-tertiary)",
                      lineHeight: 1.5,
                      flex: 1,
                    }}
                  >
                    {formula.description.length > 120
                      ? formula.description.slice(0, 120) + "..."
                      : formula.description}
                  </p>
                  <div
                    className="latex-block"
                    style={{
                      marginTop: "var(--space-md)",
                      marginBottom: 0,
                      fontSize: "0.8rem",
                      padding: "var(--space-sm) var(--space-md)",
                      textAlign: "center",
                      overflow: "hidden",
                      textOverflow: "ellipsis",
                      whiteSpace: "nowrap",
                    }}
                  >
                    {formula.formula_latex}
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </section>
      )}

      {/* ── Footer ──────────────────────────────────────────── */}
      <footer
        style={{
          padding: "var(--space-xl)",
          borderTop: "1px solid var(--border-secondary)",
          textAlign: "center",
        }}
      >
        <p
          style={{
            fontSize: "0.75rem",
            color: "var(--text-muted)",
          }}
        >
          Troy Engineering Copilot — Never skip calculations. Never provide
          black-box outputs.
        </p>
      </footer>
    </div>
  );
}
