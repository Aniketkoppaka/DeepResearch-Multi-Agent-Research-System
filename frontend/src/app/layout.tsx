import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Kairo — Autonomous AI Research System",
  description: "Enterprise-grade multi-agent autonomous research and grounding workspace",
  icons: {
    icon: "/favicon.ico",
    shortcut: "/kairo-icon.png",
    apple: "/apple-touch-icon.png",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <link rel="icon" href="/favicon.ico" sizes="any" />
      </head>
      <body>{children}</body>
    </html>
  );
}
