import DomainWorkspace from "@/components/DomainWorkspace";

export default function DronesPage() {
  return (
    <DomainWorkspace
      domain={{
        id: "drones",
        name: "Drones & UAV Engineering",
        icon: "🚁",
        color: "var(--accent-drones)",
        badgeClass: "badge-drones",
      }}
    />
  );
}
