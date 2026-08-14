import type { ReactNode } from "react";

import { Sidebar } from "./sidebar";

export function AppShell({ children }: { children: ReactNode }) {
  return (
    <div className="app-shell">
      <Sidebar />
      <div className="app-workspace">
        <header className="topbar">
          <div>
            <span className="topbar-label">工作空间</span>
            <strong>默认组织</strong>
          </div>
          <div className="topbar-user" aria-label="当前用户">
            <span aria-hidden="true">管</span>
            <div><strong>管理员</strong><small>本地工作台</small></div>
          </div>
        </header>
        <main className="workspace-content">{children}</main>
      </div>
    </div>
  );
}
