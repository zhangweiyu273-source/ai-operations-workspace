"use client";

import { useCallback, useEffect, useState } from "react";
import { ErrorState } from "@/components/ui/error-state";
import { LoadingState } from "@/components/ui/loading-state";
import { PageHeader } from "@/components/ui/page-header";
import { apiClient } from "@/lib/api/client";

type Dashboard = {
  tasks: { today: number; in_progress: number; overdue: number; pending_review: number };
  content: { total: number; pending_creation: number; in_production: number; published: number };
  keywords: { total: number; high_commercial_intent: number; unused: number; recently_added: number };
  accounts: { total: number; platform_distribution: Record<string, number>; recently_updated: { id: string; account_name: string; platform: string; updated_at: string } | null };
  knowledge: { total: number; category_count: number; recently_updated: { id: string; title: string; category: string; updated_at: string } | null };
  today_tasks: { id: string; title: string; task_type: string; account_name: string | null; topic_title: string | null; priority: string; status: string; deadline: string | null; is_overdue: boolean }[];
  review_reminders: { id: string; title: string; task_title: string | null; review_date: string; problem_summary: string | null }[];
};

function DashboardCard({ label, value, tone = "default" }: { label: string; value: number; tone?: "default" | "warning" }) {
  return <div className={`metric-card dashboard-card ${tone === "warning" ? "dashboard-warning" : ""}`}><span>{label}</span><strong>{value}</strong></div>;
}

function Overview({ title, children }: { title: string; children: React.ReactNode }) {
  return <section className="dashboard-section"><h2>{title}</h2>{children}</section>;
}

export function DashboardPage() {
  const [data, setData] = useState<Dashboard | null>(null);
  const [error, setError] = useState<string | null>(null);
  const load = useCallback(async () => {
    setError(null);
    try { setData(await apiClient.get<Dashboard>("/dashboard")); }
    catch { setError("首页数据加载失败，请稍后重试。"); }
  }, []);
  useEffect(() => {
    const timer = window.setTimeout(() => { void load(); }, 0);
    return () => window.clearTimeout(timer);
  }, [load]);

  if (!data && !error) return <LoadingState label="正在加载运营驾驶舱…" />;
  if (!data) return <ErrorState message={error ?? "首页数据加载失败"} />;
  const platforms = Object.entries(data.accounts.platform_distribution);
  return <>
    <PageHeader title="运营首页" description="聚合今天的执行进度、内容资产与需要关注的复盘事项。" actions={<button className="button secondary" onClick={() => void load()}>刷新数据</button>} />
    <section aria-label="任务概览"><div className="metric-grid dashboard-metrics"><DashboardCard label="今日任务" value={data.tasks.today} /><DashboardCard label="进行中任务" value={data.tasks.in_progress} /><DashboardCard label="逾期任务" value={data.tasks.overdue} tone="warning" /><DashboardCard label="待复盘任务" value={data.tasks.pending_review} /></div></section>
    <div className="dashboard-overview-grid">
      <Overview title="内容运营"><div className="dashboard-stat-list"><span>选题总量 <strong>{data.content.total}</strong></span><span>待创作 <strong>{data.content.pending_creation}</strong></span><span>制作中 <strong>{data.content.in_production}</strong></span><span>已发布 <strong>{data.content.published}</strong></span></div></Overview>
      <Overview title="关键词资产"><div className="dashboard-stat-list"><span>关键词总量 <strong>{data.keywords.total}</strong></span><span>高商业意图 <strong>{data.keywords.high_commercial_intent}</strong></span><span>未使用 <strong>{data.keywords.unused}</strong></span><span>近 7 天新增 <strong>{data.keywords.recently_added}</strong></span></div></Overview>
      <Overview title="账号运营"><div className="dashboard-stat-list"><span>账号数量 <strong>{data.accounts.total}</strong></span><span>平台分布 <strong>{platforms.map(([platform, count]) => `${platform} ${count}`).join("、") || "暂无"}</strong></span><span>最近更新 <strong>{data.accounts.recently_updated?.account_name ?? "暂无"}</strong></span></div></Overview>
      <Overview title="知识资产"><div className="dashboard-stat-list"><span>知识总量 <strong>{data.knowledge.total}</strong></span><span>分类数量 <strong>{data.knowledge.category_count}</strong></span><span>最近更新 <strong>{data.knowledge.recently_updated?.title ?? "暂无"}</strong></span></div></Overview>
    </div>
    <div className="dashboard-lists">
      <Overview title="今日任务"><div className="dashboard-list">{data.today_tasks.length ? data.today_tasks.map((task) => <a className="dashboard-row" href={`/tasks?taskId=${task.id}`} key={task.id}><div><strong>{task.title}</strong><small>{task.task_type} · {task.account_name ?? "未关联账号"} · {task.topic_title ?? "未关联选题"}</small></div><div><span className={task.is_overdue ? "dashboard-overdue" : ""}>{task.status}{task.is_overdue ? " · 已逾期" : ""}</span><small>{task.deadline ? new Date(task.deadline).toLocaleDateString("zh-CN") : "未设截止时间"}</small></div></a>) : <p className="dashboard-empty">今天暂无待处理任务。</p>}</div></Overview>
      <Overview title="复盘提醒"><div className="dashboard-list">{data.review_reminders.length ? data.review_reminders.map((review) => <a className="dashboard-row" href={`/reviews?reviewId=${review.id}`} key={review.id}><div><strong>{review.title}</strong><small>{review.task_title ?? "关联任务已不可用"} · {review.review_date}</small></div><p>{review.problem_summary}</p></a>) : <p className="dashboard-empty">暂无需要关注的复盘问题。</p>}</div></Overview>
    </div>
  </>;
}
