"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const navigation = [
  { href: "/", label: "首页", mark: "首" },
  { href: "/data", label: "数据中心", mark: "数" },
  { href: "/accounts", label: "账号矩阵", mark: "账" },
  { href: "/keywords", label: "关键词库", mark: "词" },
  { href: "/topics", label: "选题库", mark: "题" },
  { href: "/knowledge", label: "知识库", mark: "知" },
  { href: "/ai-analysis", label: "AI分析", mark: "AI" },
  { href: "/tasks", label: "任务复盘", mark: "任" },
  { href: "/settings", label: "系统设置", mark: "设" },
] as const;

function isActive(pathname: string, href: string) {
  return href === "/" ? pathname === "/" : pathname.startsWith(href);
}

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="sidebar">
      <div className="brand"><span>AI</span><div><strong>运营工作台</strong><small>Operations</small></div></div>
      <nav aria-label="主导航">
        {navigation.map((item) => (
          <Link
            className={isActive(pathname, item.href) ? "nav-link active" : "nav-link"}
            href={item.href}
            key={item.href}
            aria-current={isActive(pathname, item.href) ? "page" : undefined}
          >
            <span className="nav-mark" aria-hidden="true">{item.mark}</span>
            {item.label}
          </Link>
        ))}
      </nav>
      <div className="sidebar-footer"><span className="system-dot" />系统服务正常</div>
    </aside>
  );
}

export { navigation };
