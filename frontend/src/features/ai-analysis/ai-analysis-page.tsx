"use client";

import { FormEvent, useCallback, useEffect, useState } from "react";
import { PageHeader } from "@/components/ui/page-header";
import { EmptyState } from "@/components/ui/empty-state";
import { apiClient } from "@/lib/api/client";

type AnalysisType = "operation" | "content" | "keyword" | "topic" | "task_review";
type Account = { id: string; account_name: string; platform: string };
type Analysis = { id: string; analysis_type: AnalysisType; title: string; summary: string; result_json: Record<string, unknown>; provider: string; model: string; prompt_version: string; context_version: string; created_at: string };
const types: { value: AnalysisType; label: string }[] = [{ value: "operation", label: "综合运营分析" }, { value: "content", label: "内容表现分析" }, { value: "keyword", label: "关键词分析" }, { value: "topic", label: "选题分析" }, { value: "task_review", label: "任务与复盘分析" }];
const sections: [string, string][] = [["key_findings", "关键发现"], ["positive_signals", "表现良好"], ["risks", "风险问题"], ["possible_causes", "可能原因（待验证）"], ["recommendations", "下一步建议"], ["next_actions", "行动清单"], ["data_limitations", "数据局限"]];

export function AiAnalysisPage() {
  const [items, setItems] = useState<Analysis[]>([]); const [accounts, setAccounts] = useState<Account[]>([]); const [selected, setSelected] = useState<Analysis | null>(null);
  const [form, setForm] = useState<{ analysis_type: AnalysisType; date_start: string; date_end: string; platform: string; account_ids: string[] }>({ analysis_type: "operation", date_start: "", date_end: "", platform: "", account_ids: [] });
  const [loading, setLoading] = useState(false); const [error, setError] = useState("");
  const load = useCallback(async () => { const [history, accountList] = await Promise.all([apiClient.get<{ items: Analysis[] }>("/ai/analysis?page=1&page_size=20"), apiClient.get<{ items: Account[] }>("/accounts?page=1&page_size=100")]); setItems(history.items); setAccounts(accountList.items); }, []);
  useEffect(() => { const timer = window.setTimeout(() => { void load().catch(() => setError("分析历史加载失败。")); }, 0); return () => window.clearTimeout(timer); }, [load]);
  const run = async (event: FormEvent) => { event.preventDefault(); setLoading(true); setError(""); try { const item = await apiClient.post<Analysis>("/ai/analysis", { ...form, date_start: form.date_start || null, date_end: form.date_end || null, platform: form.platform || null }); setItems((previous) => [item, ...previous]); setSelected(item); } catch (cause) { setError(cause instanceof Error ? cause.message : "分析请求失败，请检查 AI 服务配置。"); } finally { setLoading(false); } };
  return <><PageHeader title="AI运营分析" description="基于工作台真实数据生成运营诊断与行动建议。AI只读数据，不会自动修改业务内容。" />
    <section className="account-list-card"><form className="filter-bar" onSubmit={run}><select aria-label="分析类型" value={form.analysis_type} onChange={(e) => setForm({ ...form, analysis_type: e.target.value as AnalysisType })}>{types.map((item) => <option key={item.value} value={item.value}>{item.label}</option>)}</select><input aria-label="开始日期" type="date" value={form.date_start} onChange={(e) => setForm({ ...form, date_start: e.target.value })}/><input aria-label="结束日期" type="date" value={form.date_end} onChange={(e) => setForm({ ...form, date_end: e.target.value })}/><select aria-label="平台" value={form.platform} onChange={(e) => setForm({ ...form, platform: e.target.value })}><option value="">全部平台</option>{[...new Set(accounts.map((item) => item.platform))].map((item) => <option key={item}>{item}</option>)}</select><select aria-label="账号" value={form.account_ids[0] ?? ""} onChange={(e) => setForm({ ...form, account_ids: e.target.value ? [e.target.value] : [] })}><option value="">全部账号</option>{accounts.map((item) => <option key={item.id} value={item.id}>{item.account_name}</option>)}</select><button className="button primary" disabled={loading}>{loading ? "分析中…" : "开始分析"}</button></form>{error && <p role="alert" className="error-message">{error}</p>}</section>
    {selected && <AnalysisResult item={selected} onClose={() => setSelected(null)} />}
    <section className="account-list-card"><h2>历史分析</h2>{items.length === 0 ? <EmptyState title="暂无历史分析" description="选择范围后发起一次分析，结果会持久化保存。" /> : <div className="analysis-history">{items.map((item) => <article key={item.id} className="analysis-row"><div><strong>{item.title}</strong><p>{item.summary}</p><small>{types.find((type) => type.value === item.analysis_type)?.label} · {new Date(item.created_at).toLocaleString("zh-CN")} · {item.model}</small></div><div className="row-actions"><button onClick={() => setSelected(item)}>查看</button><button className="danger-link" onClick={async () => { if (confirm("确认删除这条分析记录？")) { await apiClient.delete(`/ai/analysis/${item.id}`); setItems((old) => old.filter((value) => value.id !== item.id)); if (selected?.id === item.id) setSelected(null); } }}>删除</button></div></article>)}</div>}</section></>;
}

function AnalysisResult({ item, onClose }: { item: Analysis; onClose: () => void }) {
  const results = item.result_json;
  return <div className="dialog-backdrop"><section className="dialog analysis-dialog"><div className="dialog-header"><h2>{item.title}</h2><button onClick={onClose} aria-label="关闭">×</button></div><p className="analysis-summary">{item.summary}</p><div className="analysis-sections">{sections.map(([key, label]) => { const values = Array.isArray(results[key]) ? results[key] as string[] : []; return <section key={key}><h3>{label}</h3>{values.length ? <ul>{values.map((value, index) => <li key={index}>{value}</li>)}</ul> : <p>暂无。</p>}</section>; })}</div><p className="muted">AI置信度：{String(results.confidence ?? "低")} · Provider：{item.provider} · Prompt：{item.prompt_version} · Context：{item.context_version}</p></section></div>;
}
