"use client";

import { useState, useEffect } from "react";
import { api, FormulaResponse, CalculationResponse } from "@/lib/api";

export default function CalculationsPanel() {
    const [formulas, setFormulas] = useState<FormulaResponse[]>([]);
    const [selectedFormula, setSelectedFormula] = useState<FormulaResponse | null>(null);
    const [paramValues, setParamValues] = useState<Record<string, string>>({});
    const [result, setResult] = useState<CalculationResponse | null>(null);
    const [isCalculating, setIsCalculating] = useState(false);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        loadFormulas();
    }, []);

    async function loadFormulas() {
        try {
            const data = await api.getFormulas();
            setFormulas(data.formulas);
        } catch {
            setError("Failed to load formulas.");
        }
    }

    function selectFormula(formula: FormulaResponse) {
        setSelectedFormula(formula);
        setResult(null);
        setError(null);
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
        <div style={{ display: "flex", height: "100%", flexDirection: "column" }}>
            <div style={{ display: "flex", gap: "var(--space-md)", padding: "var(--space-md)", borderBottom: "1px solid var(--border-primary)", background: "var(--bg-tertiary)" }}>
                <select 
                    className="input" 
                    onChange={(e) => {
                        const f = formulas.find(form => form.id === e.target.value);
                        if (f) selectFormula(f);
                    }}
                    value={selectedFormula?.id || ""}
                    style={{ flex: 1 }}
                >
                    <option value="" disabled>Select a formula...</option>
                    {formulas.map(f => (
                        <option key={f.id} value={f.id}>[{f.domain}] {f.name}</option>
                    ))}
                </select>
            </div>

            <div style={{ display: "flex", flex: 1, overflow: "hidden" }}>
                {/* Inputs Pane */}
                <div style={{ width: "50%", padding: "var(--space-md)", overflowY: "auto", borderRight: "1px solid var(--border-primary)" }}>
                    {selectedFormula ? (
                        <>
                            <div style={{ marginBottom: "var(--space-lg)" }}>
                                <h3 style={{ fontSize: "1rem", fontWeight: 700, marginBottom: "var(--space-xs)" }}>{selectedFormula.name}</h3>
                                <p style={{ fontSize: "0.8125rem", color: "var(--text-tertiary)" }}>{selectedFormula.description}</p>
                            </div>
                            <div className="latex-block" style={{ fontSize: "0.875rem", padding: "var(--space-sm)", textAlign: "center" }}>
                                {selectedFormula.formula_latex}
                            </div>
                            <div style={{ marginTop: "var(--space-lg)" }}>
                                {selectedFormula.parameters.map((param) => (
                                    <div key={param.name} style={{ marginBottom: "var(--space-md)" }}>
                                        <label className="input-label">
                                            {param.description} <span className="input-unit">[{param.unit}]</span>
                                        </label>
                                        <input
                                            className="input"
                                            type="number"
                                            step="any"
                                            placeholder={`Default: ${param.default ?? 'Required'}`}
                                            value={paramValues[param.name] || ""}
                                            onChange={(e) => setParamValues({ ...paramValues, [param.name]: e.target.value })}
                                        />
                                    </div>
                                ))}
                                <button className="btn btn-primary" onClick={handleCalculate} disabled={isCalculating} style={{ width: "100%", marginTop: "var(--space-sm)" }}>
                                    {isCalculating ? "Computing..." : "Calculate"}
                                </button>
                            </div>
                        </>
                    ) : (
                        <div style={{ color: "var(--text-muted)", fontSize: "0.875rem", textAlign: "center", marginTop: "var(--space-2xl)" }}>
                            Select a formula from the dropdown to begin.
                        </div>
                    )}
                </div>

                {/* Results Pane */}
                <div style={{ width: "50%", padding: "var(--space-md)", overflowY: "auto", background: "var(--bg-primary)" }}>
                    {error && (
                        <div style={{ padding: "var(--space-sm)", background: "rgba(239, 68, 68, 0.1)", color: "var(--error)", borderRadius: "var(--radius-sm)", fontSize: "0.8125rem" }}>
                            ⚠️ {error}
                        </div>
                    )}
                    
                    {result && !result.error ? (
                        <div className="animate-fade-in">
                            <h4 style={{ fontSize: "0.875rem", fontWeight: 600, color: "var(--text-secondary)", marginBottom: "var(--space-md)" }}>Step-by-Step Trace</h4>
                            {result.steps.map((step, i) => (
                                <div key={i} style={{ marginBottom: "var(--space-md)" }}>
                                    <div style={{ fontSize: "0.8125rem", fontWeight: 500, color: "var(--text-secondary)", marginBottom: "var(--space-xs)" }}>
                                        Step {step.order}: {step.description}
                                    </div>
                                    <div className="latex-block" style={{ padding: "var(--space-sm)", margin: 0, fontSize: "0.875rem" }}>
                                        {step.latex}
                                    </div>
                                </div>
                            ))}

                            <h4 style={{ fontSize: "0.875rem", fontWeight: 600, color: "var(--text-secondary)", marginTop: "var(--space-xl)", marginBottom: "var(--space-md)" }}>Final Results</h4>
                            <div style={{ background: "var(--bg-tertiary)", borderRadius: "var(--radius-md)", border: "1px solid var(--border-secondary)" }}>
                                {Object.entries(result.results_formatted).map(([key, val]) => (
                                    <div key={key} style={{ display: "flex", justifyContent: "space-between", padding: "var(--space-sm) var(--space-md)", borderBottom: "1px solid var(--border-primary)" }}>
                                        <span style={{ fontSize: "0.8125rem", color: "var(--text-secondary)" }}>{key}</span>
                                        <span style={{ fontSize: "0.875rem", fontWeight: 700, fontFamily: "var(--font-mono)" }}>{val}</span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    ) : !error && (
                        <div style={{ color: "var(--text-muted)", fontSize: "0.875rem", textAlign: "center", marginTop: "var(--space-2xl)" }}>
                            Results will appear here.
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
