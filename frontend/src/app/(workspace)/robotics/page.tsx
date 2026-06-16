import DomainWorkspace from "@/components/DomainWorkspace";

export default function RoboticsPage() {
  return (
    <DomainWorkspace
      domain={{
        id: "robotics",
        name: "Robotics Engineering",
        icon: "🤖",
        color: "var(--accent-robotics)",
        badgeClass: "badge-robotics",
      }}
    />
  );
}
