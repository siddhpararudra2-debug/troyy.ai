import type { Metadata } from "next";
import "./globals.css";
import AuthGuard from "../components/AuthGuard";

export const metadata: Metadata = {
  title: "Troy — AI Engineering Copilot",
  description:
    "AI-powered engineering copilot for Aerospace, Drones, Robotics & Electronics. Step-by-step calculations, automatic documentation, and project memory.",
  keywords: [
    "engineering",
    "aerospace",
    "drones",
    "robotics",
    "electronics",
    "calculations",
    "copilot",
  ],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        <AuthGuard>{children}</AuthGuard>
      </body>
    </html>
  );
}
