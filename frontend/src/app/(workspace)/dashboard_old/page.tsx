"use client";

import { useState } from "react";
import ChatInterface from "@/components/ChatInterface";
import CalculationsPanel from "@/components/CalculationsPanel";
import DocumentationPanel from "@/components/DocumentationPanel";
import ReviewPanel from "@/components/ReviewPanel";

type Tab = "calculations" | "docs" | "review";

export default function DashboardPage() {
    const [activeTab, setActiveTab] = useState<Tab>("calculations");

    return (
        <div className="animate-fade-in" style={{ display: "flex", height: "100vh", overflow: "hidden" }}>
            
            {/* Left Pane: Chat Interface (35% width) */}
            <div style={{ width: "35%", minWidth: "400px", height: "100%" }}>
                <ChatInterface />
            </div>

            {/* Right Pane: Context Panels (65% width) */}
            <div style={{ flex: 1, display: "flex", flexDirection: "column", height: "100%", background: "var(--bg-primary)" }}>
                
                {/* Tabs Header */}
                <div style={{ 
                    display: "flex", 
                    alignItems: "center", 
                    padding: "0 var(--space-md)", 
                    height: "var(--topbar-height)", 
                    borderBottom: "1px solid var(--border-primary)", 
                    background: "rgba(10, 14, 23, 0.9)",
                    gap: "var(--space-md)"
                }}>
                    <button 
                        onClick={() => setActiveTab("calculations")}
                        style={{
                            background: "none",
                            border: "none",
                            padding: "var(--space-sm) var(--space-md)",
                            fontSize: "0.875rem",
                            fontWeight: 600,
                            color: activeTab === "calculations" ? "var(--text-primary)" : "var(--text-secondary)",
                            borderBottom: activeTab === "calculations" ? "2px solid var(--accent)" : "2px solid transparent",
                            cursor: "pointer",
                            transition: "all var(--transition-fast)"
                        }}
                    >
                        ⚡ Calculations
                    </button>
                    <button 
                        onClick={() => setActiveTab("docs")}
                        style={{
                            background: "none",
                            border: "none",
                            padding: "var(--space-sm) var(--space-md)",
                            fontSize: "0.875rem",
                            fontWeight: 600,
                            color: activeTab === "docs" ? "var(--text-primary)" : "var(--text-secondary)",
                            borderBottom: activeTab === "docs" ? "2px solid var(--accent)" : "2px solid transparent",
                            cursor: "pointer",
                            transition: "all var(--transition-fast)"
                        }}
                    >
                        📄 Documentation
                    </button>
                    <button 
                        onClick={() => setActiveTab("review")}
                        style={{
                            background: "none",
                            border: "none",
                            padding: "var(--space-sm) var(--space-md)",
                            fontSize: "0.875rem",
                            fontWeight: 600,
                            color: activeTab === "review" ? "var(--text-primary)" : "var(--text-secondary)",
                            borderBottom: activeTab === "review" ? "2px solid var(--accent)" : "2px solid transparent",
                            cursor: "pointer",
                            transition: "all var(--transition-fast)"
                        }}
                    >
                        ✅ Review
                    </button>
                </div>

                {/* Tab Content */}
                <div style={{ flex: 1, overflow: "hidden" }}>
                    {activeTab === "calculations" && <CalculationsPanel />}
                    {activeTab === "docs" && <DocumentationPanel />}
                    {activeTab === "review" && <ReviewPanel />}
                </div>

            </div>
        </div>
    );
}
