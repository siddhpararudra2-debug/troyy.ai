"use client";

import { useState, useEffect } from "react";
import { api, DocumentResponse } from "@/lib/api";

export default function DocumentationPanel() {
    const [documents, setDocuments] = useState<DocumentResponse[]>([]);
    const [selectedDoc, setSelectedDoc] = useState<DocumentResponse | null>(null);

    useEffect(() => {
        // Fetch global documents or from a specific project. For this UI, we'll try to fetch all docs or show a placeholder.
        loadDocs();
    }, []);

    async function loadDocs() {
        try {
            // we need a project ID to fetch docs, let's use the default project 'default'
            const data = await api.getProjectDocuments("default");
            setDocuments(data.documents);
            if (data.documents.length > 0) {
                setSelectedDoc(data.documents[0]);
            }
        } catch {
            // handle error
        }
    }

    return (
        <div style={{ display: "flex", height: "100%", flexDirection: "column" }}>
            <div style={{ display: "flex", gap: "var(--space-md)", padding: "var(--space-md)", borderBottom: "1px solid var(--border-primary)", background: "var(--bg-tertiary)" }}>
                <select 
                    className="input" 
                    onChange={(e) => {
                        const d = documents.find(doc => doc.id === e.target.value);
                        if (d) setSelectedDoc(d);
                    }}
                    value={selectedDoc?.id || ""}
                    style={{ flex: 1 }}
                >
                    <option value="" disabled>Select a document...</option>
                    {documents.map(d => (
                        <option key={d.id} value={d.id}>{d.title} ({d.doc_type})</option>
                    ))}
                </select>
                <button className="btn btn-secondary" onClick={loadDocs}>Refresh</button>
            </div>

            <div style={{ flex: 1, padding: "var(--space-xl)", overflowY: "auto", background: "var(--bg-primary)" }}>
                {selectedDoc ? (
                    <div className="animate-fade-in" style={{ maxWidth: 800, margin: "0 auto" }}>
                        <h2 style={{ fontSize: "1.5rem", fontWeight: 800, marginBottom: "var(--space-lg)" }}>{selectedDoc.title}</h2>
                        <div style={{ fontSize: "0.875rem", lineHeight: 1.7, color: "var(--text-secondary)", whiteSpace: "pre-wrap" }}>
                            {/* In a real app, use react-markdown to render this */}
                            {selectedDoc.content}
                        </div>
                    </div>
                ) : (
                    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", height: "100%", color: "var(--text-muted)", fontSize: "0.875rem" }}>
                        <span style={{ fontSize: "2rem", marginBottom: "var(--space-md)", opacity: 0.5 }}>📄</span>
                        No documents found. Run calculations to generate reports.
                    </div>
                )}
            </div>
        </div>
    );
}
