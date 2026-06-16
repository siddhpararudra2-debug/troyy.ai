import DomainWorkspace from "@/components/DomainWorkspace";

export default function AerospacePage() {
  return (
    <DomainWorkspace
      domain={{
        id: "aerospace",
        name: "Aerospace Engineering",
        icon: "✈️",
        color: "var(--accent-aerospace)",
        badgeClass: "badge-aerospace",
      }}
    />
  );
}
