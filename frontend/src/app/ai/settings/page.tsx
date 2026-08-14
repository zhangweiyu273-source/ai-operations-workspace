"use client";

import { FormEvent, useCallback, useEffect, useState } from "react";
import { PageHeader } from "@/components/ui/page-header";
import { apiClient } from "@/lib/api/client";

type Status = { configured: boolean; provider: string; model: string | null; provider_status: string };
type Statistics = { today_calls: number; success_count: number; failure_count: number; total_tokens: number; average_latency_ms: number | null };
type Result = { provider: string; model: string; content: string; usage?: { total_tokens?: number }; latency_ms?: number };

export default function AISettingsPage() {
  const [status, setStatus] = useState<Status | null>(null); const [stats, setStats] = useState<Statistics | null>(null); const [result, setResult] = useState<Result | null>(null); const [error, setError] = useState(""); const [busy, setBusy] = useState(false);
  const load = useCallback(async () => { const [nextStatus, nextStats] = await Promise.all([apiClient.get<Status>("/ai/status"), apiClient.get<Statistics>("/ai/statistics")]); setStatus(nextStatus); setStats(nextStats); }, []);
  useEffect(() => { const timer = window.setTimeout(() => { void load().catch(() => setError("AI 配置状态加载失败")); }, 0); return () => window.clearTimeout(timer); }, [load]);
  async function submit(event: FormEvent) { event.preventDefault(); setBusy(true); setError(""); try { setResult(await apiClient.post<Result>("/ai/test", { message: "请回复：AI运营工作台连接测试成功。" })); await load(); } catch { setError("AI 测试请求失败。请确认服务端已配置有效的 DeepSeek API Key。"); } finally { setBusy(false); } }
  return <><PageHeader title="AI Provider 设置" description="仅用于验证服务端 AI Provider 配置；密钥不会在浏览器显示或保存。" /><section className="account-list-card"><div className="metric-grid"><div className="metric-card"><span>配置状态</span><strong>{status?.configured ? "已配置" : "未配置"}</strong></div><div className="metric-card"><span>Provider / 模型</span><strong>{status ? `${status.provider} / ${status.model ?? "-"}` : "-"}</strong></div><div className="metric-card"><span>今日调用</span><strong>{stats?.today_calls ?? "-"}</strong></div></div><p>成功 {stats?.success_count ?? 0} · 失败 {stats?.failure_count ?? 0} · Token {stats?.total_tokens ?? 0} · 平均耗时 {stats?.average_latency_ms?.toFixed(0) ?? "-"}ms</p><form onSubmit={submit}><button className="button primary" disabled={busy || !status?.configured}>{busy ? "测试中…" : "测试 AI Provider"}</button></form>{error && <p role="alert" className="error-message">{error}</p>}{result && <div className="reserved-data"><strong>{result.provider} / {result.model}</strong><p>{result.content}</p><p>Token：{result.usage?.total_tokens ?? "-"}，耗时：{result.latency_ms ?? "-"}ms</p></div>}</section></>;
}
