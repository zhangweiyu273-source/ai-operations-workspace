import type { Metadata } from "next";
import { headers } from "next/headers";
import { AppShell } from "@/components/layout/app-shell";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI运营工作台",
  description: "教培行业 AI 运营中台",
};

export default async function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  const requestHeaders = await headers();
  const isReadOnly = requestHeaders.get("x-ai-ops-role") === "viewer";

  return (
    <html lang="zh-CN">
      <body><AppShell readOnly={isReadOnly}>{children}</AppShell></body>
    </html>
  );
}
