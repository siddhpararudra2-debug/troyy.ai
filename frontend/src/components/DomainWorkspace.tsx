"use client";

import { useState, useEffect, useCallback } from "react";
import {
  api,
  FormulaResponse,
  CalculationResponse,
  CalculationStep,
} from "@/lib/api";

/* ── Domain Config ────────────────────────────────────────────── */
interface DomainConfig {
  id: string;
  name: string;
  icon: string;
  color: string;
  badgeClass: string;
}

/* ── Props ────────────────────────────────────────────────────── */
interface DomainWorkspaceProps {
  domain: DomainConfig;
}

/* ── Main Component ───────────────────────────────────────────── */
export default function DomainWorkspace({ domain }: DomainWorkspaceProps) {
  const [formulas, setFormulas] = useState<FormulaResponse[]>([]);
  const [selectedFormula, setSelectedFormula] = useState<FormulaResponse | null>(null);
  const [paramValues, setParamValues] = useState<Record<string, string>>({});
  const [result, setResult] = useState<CalculationResponse | null>(null);
  const [isCalculating, setIsCalculating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadFormulas();
  }, [domain.id]);

  async function loadFormulas() {
    try {
      const data = await api.getFormulas({ domain: domain.id });
      setFormulas(data.formulas);
      if (data.formulas.length > 0) {
        selectFormula(data.formulas[0]);
      }
    } catch {
      setError("Failed to load formulas. Is the backend running?");
    }
  }

  function selectFormula(formula: FormulaResponse) {
    setSelectedFormula(formula);
    setResult(null);
    setError(null);

    // Pre-fill defaults
    const defaults: Record<string, string> = {};
    formula.parameters.forEach((p) => {
      if (p.default !== null && p.default !== undefined) {
        defaults[p.name] = String(p.default);
      } else {
        defaults[p.name] = "";
      }
    });
    setParamValues(defaults);
  }

  async function handleCalculate() {
    if (!selectedFormula) return;

    setIsCalculating(true);
    setError(null);

    try {
      const params: Record<string, number> = {};
      for (const p of selectedFormula.parameters) {
        const val = parseFloat(paramValues[p.name] || "");
        if (isNaN(val) && p.default === null) {
          setError(`Parameter "${p.name}" requires a numeric value`);
          setIsCalculating(false);
          return;
        }
        if (!isNaN(val)) {
          params[p.name] = val;
        }
      }

      const calcResult = await api.calculate({
        formula_id: selectedFormula.id,
        parameters: params,
      });

      setResult(calcResult);

      if (calcResult.error) {
        setError(calcResult.error);
      }
    } catch (e: unknown) {
      const err = e as { detail?: string };
      setError(err?.detail || "Calculation failed");
    } finally {
      setIsCalculating(false);
    }
  }

  return (
    <div className="animate-fade-in" style={{ padding: "var(--space-xl)" }}>
      {/* ── Header ──────────────────────────────────────────── */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: "var(--space-md)",
          marginBottom: "var(--space-xl)",
        }}
      >
        <span style={{ fontSize: "2rem" }}>{domain.icon}</span>
        <div>
          <h1 style={{ fontSize: "1.5rem", fontWeight: 800 }}>{domain.name}</h1>
          <p style={{ fontSize: "0.8125rem", color: "var(--text-tertiary)" }}>
            {formulas.length} formulas available
          </p>
        </div>
      </div>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "280px 1fr 1fr",
          gap: "var(--space-lg)",
          alignItems: "start",
        }}
      >
        {/* ── Formula Selector (Left Panel) ─────────────────── */}
        <div
          className="glass-card"
          style={{ padding: "var(--space-md)", maxHeight: "80vh", overflowY: "auto" }}
        >
          <h3
            style={{
              fontSize: "0.8125rem",
              fontWeight: 600,
              color: "var(--text-tertiary)",
              textTransform: "uppercase",
              letterSpacing: "0.06em",
              marginBottom: "var(--space-md)",
              padding: "0 var(--space-sm)",
            }}
          >
            Formulas
          </h3>

          {formulas.map((formula) => (
            <button
              key={formula.id}
              onClick={() => selectFormula(formula)}
              style={{
                display: "block",
                width: "100%",
                textAlign: "left",
                padding: "var(--space-md)",
                borderRadius: "var(--radius-md)",
                border: "none",
                cursor: "pointer",
                marginBottom: "var(--space-xs)",
                background:
                  selectedFormula?.id === formula.id
                    ? "rgba(59, 130, 246, 0.12)"
                    : "transparent",
                borderLeft:
                  selectedFormula?.id === formula.id
                    ? `3px solid ${domain.color}`
                    : "3px solid transparent",
                transition: "all var(--transition-fast)",
                fontFamily: "var(--font-sans)",
              }}
            >
              <div
                style={{
                  fontSize: "0.8125rem",
                  fontWeight: 600,
                  color:
                    selectedFormula?.id === formula.id
                      ? "var(--text-primary)"
                      : "var(--text-secondary)",
                  marginBottom: 2,
                }}
              >
                {formula.name}
              </div>
              <div
                style={{
                  fontSize: "0.6875rem",
                  color: "var(--text-muted)",
                  fontFamily: "var(--font-mono)",
                }}
              >
                {formula.category}
              </div>
            </button>
          ))}

          {formulas.length === 0 && (
            <p
              style={{
                fontSize: "0.8125rem",
                color: "var(--text-muted)",
                padding: "var(--space-lg)",
                textAlign: "center",
              }}
            >
              No formulas loaded. <br />
              Start the backend first.
            </p>
          )}
        </div>

        {/* ── Input Panel (Center) ──────────────────────────── */}
        <div className="glass-card" style={{ minHeight: 400 }}>
          {selectedFormula ? (
            <>
              <div style={{ marginBottom: "var(--space-lg)" }}>
                <span className={`badge ${domain.badgeClass}`} style={{ marginBottom: "var(--space-sm)", display: "inline-block" }}>
                  {selectedFormula.category}
                </span>
                <h2
                  style={{
                    fontSize: "1.25rem",
                    fontWeight: 700,
                    marginBottom: "var(--space-xs)",
                  }}
                >
                  {selectedFormula.name}
                </h2>
                <p
                  style={{
                    fontSize: "0.8125rem",
                    color: "var(--text-tertiary)",
                    lineHeight: 1.6,
                  }}
                >
                  {selectedFormula.description}
                </p>
              </div>

              {/* Formula display */}
              <div className="latex-block" style={{ textAlign: "center", fontSize: "1rem", marginBottom: "var(--space-lg)" }}>
                {selectedFormula.formula_latex}
              </div>

              {/* Parameter inputs */}
              <div style={{ marginBottom: "var(--space-lg)" }}>
                <h3
                  style={{
                    fontSize: "0.8125rem",
                    fontWeight: 600,
                    color: "var(--text-tertiary)",
                    textTransform: "uppercase",
                    letterSpacing: "0.06em",
                    marginBottom: "var(--space-md)",
                  }}
                >
                  Parameters
                </h3>

                {selectedFormula.parameters.map((param) => (
                  <div
                    key={param.name}
                    style={{ marginBottom: "var(--space-md)" }}
                  >
                    <label className="input-label">
                      {param.description}
                      <span className="input-unit">[{param.unit}]</span>
                      {param.min_value !== null && param.max_value !== null && (
                        <span
                          style={{
                            fontSize: "0.6875rem",
                            color: "var(--text-muted)",
                            marginLeft: "var(--space-sm)",
                            fontFamily: "var(--font-mono)",
                          }}
                        >
                          ({param.min_value} — {param.max_value})
                        </span>
                      )}
                    </label>
                    <input
                      className="input"
                      type="number"
                      step="any"
                      placeholder={
                        param.default !== null
                          ? `Default: ${param.default}`
                          : `Enter ${param.name}`
                      }
                      value={paramValues[param.name] || ""}
                      onChange={(e) =>
                        setParamValues({
                          ...paramValues,
                          [param.name]: e.target.value,
                        })
                      }
                    />
                  </div>
                ))}
              </div>

              {/* Calculate button */}
              <button
                className="btn btn-primary btn-lg"
                onClick={handleCalculate}
                disabled={isCalculating}
                style={{
                  width: "100%",
                  opacity: isCalculating ? 0.7 : 1,
                }}
              >
                {isCalculating ? "⏳ Computing..." : "⚡ Calculate"}
              </button>

              {/* Reference */}
              {selectedFormula.reference && (
                <p
                  style={{
                    fontSize: "0.6875rem",
                    color: "var(--text-muted)",
                    marginTop: "var(--space-md)",
                    fontStyle: "italic",
                  }}
                >
                  📚 {selectedFormula.reference}
                </p>
              )}
            </>
          ) : (
            <div
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                height: 300,
                color: "var(--text-muted)",
                fontSize: "0.875rem",
              }}
            >
              Select a formula to begin
            </div>
          )}
        </div>

        {/* ── Results Panel (Right) ─────────────────────────── */}
        <div className="glass-card" style={{ minHeight: 400 }}>
          <h3
            style={{
              fontSize: "0.8125rem",
              fontWeight: 600,
              color: "var(--text-tertiary)",
              textTransform: "uppercase",
              letterSpacing: "0.06em",
              marginBottom: "var(--space-lg)",
            }}
          >
            Results
          </h3>

          {error && (
            <div
              style={{
                padding: "var(--space-md)",
                background: "rgba(239, 68, 68, 0.1)",
                border: "1px solid rgba(239, 68, 68, 0.2)",
                borderRadius: "var(--radius-md)",
                marginBottom: "var(--space-lg)",
                fontSize: "0.8125rem",
                color: "var(--error)",
              }}
            >
              ⚠️ {error}
            </div>
          )}

          {result && !result.error && (
            <div className="animate-fade-in">
              {/* Execution info */}
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  marginBottom: "var(--space-lg)",
                  padding: "var(--space-sm) var(--space-md)",
                  background: "rgba(16, 185, 129, 0.08)",
                  borderRadius: "var(--radius-md)",
                  border: "1px solid rgba(16, 185, 129, 0.15)",
                }}
              >
                <span
                  style={{
                    fontSize: "0.75rem",
                    fontWeight: 600,
                    color: "var(--success)",
                  }}
                >
                  ✓ Calculation complete
                </span>
                <span
                  style={{
                    fontSize: "0.6875rem",
                    color: "var(--text-muted)",
                    fontFamily: "var(--font-mono)",
                  }}
                >
                  {result.execution_time_ms.toFixed(2)} ms
                </span>
              </div>

              {/* Warnings */}
              {result.warnings.length > 0 && (
                <div
                  style={{
                    marginBottom: "var(--space-lg)",
                    padding: "var(--space-sm) var(--space-md)",
                    background: "rgba(245, 158, 11, 0.08)",
                    borderRadius: "var(--radius-md)",
                    border: "1px solid rgba(245, 158, 11, 0.15)",
                  }}
                >
                  {result.warnings.map((w, i) => (
                    <p
                      key={i}
                      style={{
                        fontSize: "0.75rem",
                        color: "var(--warning)",
                        marginBottom: 2,
                      }}
                    >
                      ⚠ {w}
                    </p>
                  ))}
                </div>
              )}

              {/* Step-by-step results */}
              <div style={{ marginBottom: "var(--space-lg)" }}>
                <h4
                  style={{
                    fontSize: "0.8125rem",
                    fontWeight: 600,
                    marginBottom: "var(--space-md)",
                    color: "var(--text-secondary)",
                  }}
                >
                  Step-by-Step Solution
                </h4>

                {result.steps.map((step, i) => (
                  <div
                    key={i}
                    style={{
                      marginBottom: "var(--space-md)",
                      animation: `fadeIn 0.3s ease-out ${i * 80}ms both`,
                    }}
                  >
                    <div className="step-indicator">
                      <div
                        className="step-number"
                        style={{
                          background:
                            step.step_type === "result"
                              ? "var(--success)"
                              : step.step_type === "substitution"
                              ? domain.color
                              : "var(--accent)",
                        }}
                      >
                        {step.order}
                      </div>
                      <span
                        style={{
                          fontSize: "0.8125rem",
                          fontWeight: 500,
                          color: "var(--text-secondary)",
                        }}
                      >
                        {step.description}
                      </span>
                    </div>
                    <div
                      className="latex-block"
                      style={{ marginLeft: 36, marginTop: 0 }}
                    >
                      {step.latex}
                    </div>
                  </div>
                ))}
              </div>

              {/* Final results table */}
              <div>
                <h4
                  style={{
                    fontSize: "0.8125rem",
                    fontWeight: 600,
                    marginBottom: "var(--space-md)",
                    color: "var(--text-secondary)",
                  }}
                >
                  Final Results
                </h4>
                <div
                  style={{
                    background: "rgba(10, 14, 23, 0.6)",
                    borderRadius: "var(--radius-md)",
                    border: "1px solid var(--border-primary)",
                    overflow: "hidden",
                  }}
                >
                  {Object.entries(result.results_formatted).map(
                    ([key, value], i) => (
                      <div
                        key={key}
                        style={{
                          display: "flex",
                          justifyContent: "space-between",
                          padding: "var(--space-md)",
                          borderBottom:
                            i <
                            Object.keys(result.results_formatted).length - 1
                              ? "1px solid var(--border-secondary)"
                              : "none",
                        }}
                      >
                        <span
                          style={{
                            fontSize: "0.8125rem",
                            fontWeight: 500,
                            color: "var(--text-secondary)",
                          }}
                        >
                          {key}
                        </span>
                        <span
                          style={{
                            fontSize: "0.875rem",
                            fontWeight: 700,
                            color: "var(--text-primary)",
                            fontFamily: "var(--font-mono)",
                          }}
                        >
                          {value}
                        </span>
                      </div>
                    )
                  )}
                </div>
              </div>
            </div>
          )}

          {!result && !error && (
            <div
              style={{
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                justifyContent: "center",
                height: 300,
                color: "var(--text-muted)",
                fontSize: "0.875rem",
                gap: "var(--space-sm)",
              }}
            >
              <span style={{ fontSize: "2rem", opacity: 0.3 }}>📊</span>
              Results will appear here
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
