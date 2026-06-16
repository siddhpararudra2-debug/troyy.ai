import DomainWorkspace from "@/components/DomainWorkspace";

export default function ElectronicsPage() {
  return (
    <DomainWorkspace
      domain={{
        id: "electronics",
        name: "Electronics Engineering",
        icon: "⚡",
        color: "var(--accent-electronics)",
        badgeClass: "badge-electronics",
      }}
    />
  );
}
