"use client";

import { useState, useEffect } from "react";
import { api, ProjectResponse } from "@/lib/api";

export default function ProjectsPage() {
  const [projects, setProjects] = useState<ProjectResponse[]>([]);
  const [showCreate, setShowCreate] = useState(false);
  const [newName, setNewName] = useState("");
  const [newDesc, setNewDesc] = useState("");
  const [newDomain, setNewDomain] = useState("multi");

  useEffect(() => {
    loadProjects();
  }, []);

  async function loadProjects() {
    try {
      const data = await api.getProjects();
      setProjects(data.projects);
    } catch {
      // Backend offline
    }
  }

  async function handleCreate() {
    if (!newName.trim()) return;
    try {
      await api.createProject({
        name: newName,
        description: newDesc,
        domain: newDomain,
      });
      setNewName("");
      setNewDesc("");
      setNewDomain("multi");
      setShowCreate(false);
      loadProjects();
    } catch {
      // Handle error
    }
  }

  const domainColors: Record<string, string> = {
    aerospace: "var(--accent-aerospace)",
    drones: "var(--accent-drones)",
    robotics: "var(--accent-robotics)",
    electronics: "var(--accent-electronics)",
    multi: "var(--accent)",
  };

  return (
    <div className="animate-fade-in" style={{ padding: "var(--space-xl)" }}>
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          marginBottom: "var(--space-xl)",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "var(--space-md)" }}>
          <span style={{ fontSize: "2rem" }}>📁</span>
          <div>
            <h1 style={{ fontSize: "1.5rem", fontWeight: 800 }}>Projects</h1>
            <p style={{ fontSize: "0.8125rem", color: "var(--text-tertiary)" }}>
              {projects.length} project{projects.length !== 1 ? "s" : ""}
            </p>
          </div>
        </div>
        <button
          className="btn btn-primary"
          onClick={() => setShowCreate(!showCreate)}
        >
          + New Project
        </button>
      </div>

      {/* Create project form */}
      {showCreate && (
        <div
          className="glass-card animate-fade-in"
          style={{ marginBottom: "var(--space-xl)" }}
        >
          <h3
            style={{
              fontSize: "1rem",
              fontWeight: 700,
              marginBottom: "var(--space-lg)",
            }}
          >
            Create New Project
          </h3>
          <div style={{ marginBottom: "var(--space-md)" }}>
            <label className="input-label">Project Name</label>
            <input
              className="input"
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
              placeholder="e.g., Quadcopter Design v2"
            />
          </div>
          <div style={{ marginBottom: "var(--space-md)" }}>
            <label className="input-label">Description</label>
            <input
              className="input"
              value={newDesc}
              onChange={(e) => setNewDesc(e.target.value)}
              placeholder="Brief project description"
            />
          </div>
          <div style={{ marginBottom: "var(--space-lg)" }}>
            <label className="input-label">Domain</label>
            <select
              className="input"
              value={newDomain}
              onChange={(e) => setNewDomain(e.target.value)}
            >
              <option value="multi">Multi-domain</option>
              <option value="aerospace">Aerospace</option>
              <option value="drones">Drones & UAV</option>
              <option value="robotics">Robotics</option>
              <option value="electronics">Electronics</option>
            </select>
          </div>
          <div style={{ display: "flex", gap: "var(--space-md)" }}>
            <button className="btn btn-primary" onClick={handleCreate}>
              Create Project
            </button>
            <button
              className="btn btn-ghost"
              onClick={() => setShowCreate(false)}
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* Project list */}
      <div className="grid-3">
        {projects.map((project) => (
          <div key={project.id} className="glass-card">
            <div
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                marginBottom: "var(--space-md)",
              }}
            >
              <span
                className={`badge badge-${project.domain}`}
                style={
                  project.domain === "multi"
                    ? {
                        background: "var(--accent-subtle)",
                        color: "var(--accent)",
                        border: "1px solid rgba(59, 130, 246, 0.2)",
                      }
                    : undefined
                }
              >
                {project.domain}
              </span>
              <div
                style={{
                  width: 8,
                  height: 8,
                  borderRadius: "50%",
                  background:
                    project.status === "active"
                      ? "var(--success)"
                      : "var(--text-muted)",
                }}
              />
            </div>

            <h3
              style={{
                fontSize: "1rem",
                fontWeight: 700,
                marginBottom: "var(--space-xs)",
              }}
            >
              {project.name}
            </h3>
            {project.description && (
              <p
                style={{
                  fontSize: "0.8125rem",
                  color: "var(--text-tertiary)",
                  marginBottom: "var(--space-md)",
                  lineHeight: 1.5,
                }}
              >
                {project.description}
              </p>
            )}

            <div
              style={{
                display: "flex",
                gap: "var(--space-lg)",
                fontSize: "0.75rem",
                color: "var(--text-muted)",
              }}
            >
              <span>📐 {project.calculation_count} calcs</span>
              <span>📄 {project.document_count} docs</span>
            </div>
          </div>
        ))}
      </div>

      {projects.length === 0 && (
        <div
          style={{
            textAlign: "center",
            padding: "var(--space-3xl)",
            color: "var(--text-muted)",
          }}
        >
          <p style={{ fontSize: "2rem", marginBottom: "var(--space-md)" }}>📁</p>
          <p>No projects yet. Create one to get started.</p>
        </div>
      )}
    </div>
  );
}
