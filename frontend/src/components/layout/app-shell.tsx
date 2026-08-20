import type { ReactNode } from "react";

import { Sidebar } from "./sidebar";

export function AppShell({ children, readOnly = false }: { children: ReactNode; readOnly?: boolean }) {
  return (
    <div className="app-shell" data-read-only={readOnly || undefined}>
      <Sidebar />
      <div className="app-workspace">
        <header className="topbar">
          <div>
            <span className="topbar-label">工作空间</span>
            <strong>默认组织</strong>
          </div>
          <div className="topbar-user" aria-label="当前用户">
            <span aria-hidden="true">管</span>
            <div><strong>{readOnly ? "只读访客" : "管理员"}</strong><small>{readOnly ? "只读查看模式" : "本地工作台"}</small></div>
          </div>
        </header>
        <main className="workspace-content">
          {readOnly ? <p className="read-only-notice" role="status">当前为只读模式：可查看数据与分析，不能新增、编辑、删除或运行 AI 操作。</p> : null}
          {children}
        </main>
      </div>
    </div>
  );
}
