"use client";

import { useState } from "react";

export default function ReviewPanel() {
    const [entries, setEntries] = useState([
        { id: 1, type: "constraint", content: "Max thrust-to-weight ratio cannot exceed 2.5 due to battery discharge limits.", status: "approved" },
        { id: 2, type: "assumption", content: "Hover efficiency assumed to be 70% for standard 10-inch props.", status: "pending" },
    ]);

    return (
        <div style={{ display: "flex", height: "100%", flexDirection: "column", background: "var(--bg-primary)" }}>
            <div style={{ padding: "var(--space-md)", borderBottom: "1px solid var(--border-primary)", background: "var(--bg-tertiary)" }}>
                <h3 style={{ fontSize: "0.875rem", fontWeight: 600 }}>Design Review & Constraints</h3>
                <p style={{ fontSize: "0.75rem", color: "var(--text-tertiary)" }}>Review assumptions and parameters suggested by the AI.</p>
            </div>

            <div style={{ flex: 1, padding: "var(--space-md)", overflowY: "auto" }}>
                {entries.map(entry => (
                    <div key={entry.id} style={{ 
                        padding: "var(--space-md)", 
                        background: "var(--bg-card)", 
                        border: "1px solid var(--border-secondary)", 
                        borderRadius: "var(--radius-md)", 
                        marginBottom: "var(--space-md)",
                        borderLeft: `3px solid ${entry.type === 'constraint' ? 'var(--error)' : 'var(--warning)'}`
                    }}>
                        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "var(--space-sm)" }}>
                            <span style={{ fontSize: "0.6875rem", textTransform: "uppercase", fontWeight: 700, color: "var(--text-secondary)" }}>
                                {entry.type}
                            </span>
                            <span className={`badge ${entry.status === 'approved' ? 'badge-drones' : 'badge-aerospace'}`}>
                                {entry.status}
                            </span>
                        </div>
                        <p style={{ fontSize: "0.875rem", color: "var(--text-primary)", marginBottom: "var(--space-md)" }}>
                            {entry.content}
                        </p>
                        {entry.status === 'pending' && (
                            <div style={{ display: "flex", gap: "var(--space-sm)" }}>
                                <button className="btn btn-primary btn-sm" onClick={() => setEntries(entries.map(e => e.id === entry.id ? { ...e, status: 'approved' } : e))}>Approve</button>
                                <button className="btn btn-secondary btn-sm" onClick={() => setEntries(entries.filter(e => e.id !== entry.id))}>Reject</button>
                            </div>
                        )}
                    </div>
                ))}

                {entries.length === 0 && (
                    <div style={{ color: "var(--text-muted)", fontSize: "0.875rem", textAlign: "center", marginTop: "var(--space-2xl)" }}>
                        No pending reviews.
                    </div>
                )}
            </div>
        </div>
    );
}
