"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const NAV_ITEMS = [
  { href: "/aerospace", label: "Aerospace", icon: "✈️", color: "var(--accent-aerospace)" },
  { href: "/drones", label: "Drones", icon: "🚁", color: "var(--accent-drones)" },
  { href: "/robotics", label: "Robotics", icon: "🤖", color: "var(--accent-robotics)" },
  { href: "/electronics", label: "Electronics", icon: "⚡", color: "var(--accent-electronics)" },
];

export default function WorkspaceLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();

  return (
    <div style={{ display: "flex", minHeight: "100vh", position: "relative", zIndex: 1 }}>
      {/* ── Sidebar ─────────────────────────────────────────── */}
      <aside
        style={{
          width: "var(--sidebar-width)",
          background: "rgba(10, 14, 23, 0.9)",
          backdropFilter: "blur(16px)",
          borderRight: "1px solid var(--border-primary)",
          display: "flex",
          flexDirection: "column",
          position: "fixed",
          top: 0,
          bottom: 0,
          left: 0,
          zIndex: 50,
        }}
      >
        {/* Logo */}
        <Link
          href="/"
          style={{
            display: "flex",
            alignItems: "center",
            gap: "var(--space-md)",
            padding: "var(--space-lg) var(--space-lg)",
            textDecoration: "none",
            color: "inherit",
            borderBottom: "1px solid var(--border-secondary)",
          }}
        >
          <div
            style={{
              width: 32,
              height: 32,
              borderRadius: "var(--radius-sm)",
              background: "linear-gradient(135deg, var(--accent), #8b5cf6)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: "0.875rem",
              fontWeight: 800,
              color: "white",
            }}
          >
            T
          </div>
          <div>
            <div style={{ fontSize: "0.9375rem", fontWeight: 700 }}>Troy</div>
            <div
              style={{
                fontSize: "0.625rem",
                color: "var(--text-tertiary)",
                textTransform: "uppercase",
                letterSpacing: "0.06em",
              }}
            >
              Engineering Copilot
            </div>
          </div>
        </Link>

        {/* Navigation */}
        <nav style={{ padding: "var(--space-md)", flex: 1 }}>
          <div
            style={{
              fontSize: "0.6875rem",
              fontWeight: 600,
              color: "var(--text-muted)",
              textTransform: "uppercase",
              letterSpacing: "0.08em",
              padding: "var(--space-sm) var(--space-md)",
              marginBottom: "var(--space-xs)",
            }}
          >
            Domains
          </div>

          {NAV_ITEMS.map((item) => {
            const isActive = pathname.startsWith(item.href);
            return (
              <Link
                key={item.href}
                href={item.href}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "var(--space-md)",
                  padding: "10px var(--space-md)",
                  borderRadius: "var(--radius-md)",
                  textDecoration: "none",
                  color: isActive ? "var(--text-primary)" : "var(--text-secondary)",
                  background: isActive
                    ? "rgba(59, 130, 246, 0.1)"
                    : "transparent",
                  borderLeft: isActive
                    ? `3px solid ${item.color}`
                    : "3px solid transparent",
                  marginBottom: "var(--space-xs)",
                  transition: "all var(--transition-fast)",
                  fontSize: "0.875rem",
                  fontWeight: isActive ? 600 : 400,
                }}
              >
                <span style={{ fontSize: "1.125rem" }}>{item.icon}</span>
                {item.label}
              </Link>
            );
          })}

          <div
            style={{
              height: 1,
              background: "var(--border-secondary)",
              margin: "var(--space-lg) var(--space-md)",
            }}
          />

          <div
            style={{
              fontSize: "0.6875rem",
              fontWeight: 600,
              color: "var(--text-muted)",
              textTransform: "uppercase",
              letterSpacing: "0.08em",
              padding: "var(--space-sm) var(--space-md)",
              marginBottom: "var(--space-xs)",
            }}
          >
            Tools
          </div>

          <Link
            href="/dashboard"
            style={{
              display: "flex",
              alignItems: "center",
              gap: "var(--space-md)",
              padding: "10px var(--space-md)",
              borderRadius: "var(--radius-md)",
              textDecoration: "none",
              color: pathname === "/dashboard" ? "var(--text-primary)" : "var(--text-secondary)",
              background: pathname === "/dashboard" ? "var(--accent-subtle)" : "transparent",
              borderLeft: pathname === "/dashboard" ? "3px solid var(--accent)" : "3px solid transparent",
              marginBottom: "var(--space-xs)",
              transition: "all var(--transition-fast)",
              fontSize: "0.875rem",
            }}
          >
            <span style={{ fontSize: "1.125rem" }}>🧭</span>
            Dashboard
          </Link>

          <Link
            href="/projects"
            style={{
              display: "flex",
              alignItems: "center",
              gap: "var(--space-md)",
              padding: "10px var(--space-md)",
              borderRadius: "var(--radius-md)",
              textDecoration: "none",
              color: pathname === "/projects" ? "var(--text-primary)" : "var(--text-secondary)",
              background: pathname === "/projects" ? "var(--accent-subtle)" : "transparent",
              borderLeft: pathname === "/projects" ? "3px solid var(--accent)" : "3px solid transparent",
              marginBottom: "var(--space-xs)",
              transition: "all var(--transition-fast)",
              fontSize: "0.875rem",
            }}
          >
            <span style={{ fontSize: "1.125rem" }}>📁</span>
            Projects
          </Link>

          <Link
            href="/docs"
            style={{
              display: "flex",
              alignItems: "center",
              gap: "var(--space-md)",
              padding: "10px var(--space-md)",
              borderRadius: "var(--radius-md)",
              textDecoration: "none",
              color: pathname === "/docs" ? "var(--text-primary)" : "var(--text-secondary)",
              background: pathname === "/docs" ? "var(--accent-subtle)" : "transparent",
              borderLeft: pathname === "/docs" ? "3px solid var(--accent)" : "3px solid transparent",
              transition: "all var(--transition-fast)",
              fontSize: "0.875rem",
            }}
          >
            <span style={{ fontSize: "1.125rem" }}>📄</span>
            Documents
          </Link>
        </nav>

        {/* Footer */}
        <div
          style={{
            padding: "var(--space-md) var(--space-lg)",
            borderTop: "1px solid var(--border-secondary)",
            fontSize: "0.6875rem",
            color: "var(--text-muted)",
          }}
        >
          Troy v0.1.0 — Local Mode
        </div>
      </aside>

      {/* ── Main Content ───────────────────────────────────── */}
      <main
        style={{
          marginLeft: "var(--sidebar-width)",
          flex: 1,
          minHeight: "100vh",
        }}
      >
        {children}
      </main>
    </div>
  );
}
