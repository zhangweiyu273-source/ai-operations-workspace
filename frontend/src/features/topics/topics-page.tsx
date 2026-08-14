"use client";

import { FormEvent, useCallback, useEffect, useState } from "react";
import { PageHeader } from "@/components/ui/page-header";
import { TableContainer } from "@/components/ui/table-container";
import { apiClient } from "@/lib/api/client";

type Account = { id: string; account_name: string; platform: string };
type Keyword = { id: string; keyword: string };
type Topic = { id: string; title: string; platform: string; account_id: string; account_name: string; content_type: string; status: string; priority: string; target_user?: string; subject?: string; keyword_count: number; keyword_ids: string[]; updated_at: string };
type TopicStats = { total: number; pending_creation: number; in_production: number; published: number; reviewed: number };
type FormValue = Omit<Topic, "id" | "account_name" | "keyword_count" | "updated_at"> & { id?: string; target_user?: string; school_stage?: string; city?: string; pain_point?: string; content_goal?: string; notes?: string };

const statuses = ["待规划", "待创作", "制作中", "待发布", "已发布", "已复盘", "暂停"];
const types = ["图文", "短视频", "直播", "文章", "朋友圈"];
const priorities = ["高", "中", "低"];
const blank = (): FormValue => ({ title: "", platform: "", account_id: "", content_type: "图文", status: "待规划", priority: "中", keyword_ids: [] });

function queryString(filters: Record<string, string>) {
  const params = new URLSearchParams({ page: "1", page_size: "20" });
  Object.entries(filters).forEach(([key, value]) => value && params.set(key, value));
  return params.toString();
}

export function TopicsPage() {
  const [topics, setTopics] = useState<Topic[]>([]);
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [keywords, setKeywords] = useState<Keyword[]>([]);
  const [stats, setStats] = useState<TopicStats | null>(null);
  const [form, setForm] = useState<FormValue | null>(null);
  const [filters, setFilters] = useState({ search: "", platform: "", account_id: "", status: "", content_type: "", subject: "" });
  const [error, setError] = useState("");
  const load = useCallback(async () => {
    const query = queryString(filters);
    const [accountData, keywordData, topicData, statData] = await Promise.all([
      apiClient.get<{ items: Account[] }>("/accounts?page_size=100"),
      apiClient.get<{ items: Keyword[] }>("/keywords?page_size=100"),
      apiClient.get<{ items: Topic[] }>(`/topics?${query}`),
      apiClient.get<TopicStats>(`/topics/stats?${query}`),
    ]);
    setAccounts(accountData.items); setKeywords(keywordData.items); setTopics(topicData.items); setStats(statData);
  }, [filters]);
  useEffect(() => {
    const timer = window.setTimeout(() => { void load().catch(() => setError("选题数据加载失败，请稍后重试。")); }, 0);
    return () => window.clearTimeout(timer);
  }, [load]);
  const updateFilter = (key: keyof typeof filters, value: string) => setFilters((current) => ({ ...current, [key]: value }));
  async function save(value: FormValue) {
    if (!value.title.trim() || !value.platform || !value.account_id) { setError("请填写标题、平台和账号。"); return; }
    setError("");
    if (value.id) await apiClient.put(`/topics/${value.id}`, value); else await apiClient.post("/topics", value);
    setForm(null); await load();
  }
  return <>
    <PageHeader title="选题库" description="管理所有内容规划。" actions={<button className="button primary" onClick={() => { setError(""); setForm(blank()); }}>新增选题</button>} />
    {error && <p role="alert" className="error-message">{error}</p>}
    <section className="stat-grid">{[["选题总数", stats?.total], ["待创作", stats?.pending_creation], ["制作中", stats?.in_production], ["已发布", stats?.published], ["已复盘", stats?.reviewed]].map(([label, value]) => <div className="stat-card" key={String(label)}><span>{label}</span><strong>{value ?? "-"}</strong></div>)}</section>
    <section className="account-list-card"><div className="filter-bar">
      <input aria-label="搜索选题" placeholder="搜索标题、痛点或备注" value={filters.search} onChange={(event) => updateFilter("search", event.target.value)} />
      <select aria-label="平台筛选" value={filters.platform} onChange={(event) => updateFilter("platform", event.target.value)}><option value="">全部平台</option>{[...new Set(accounts.map((account) => account.platform))].map((value) => <option key={value}>{value}</option>)}</select>
      <select aria-label="账号筛选" value={filters.account_id} onChange={(event) => updateFilter("account_id", event.target.value)}><option value="">全部账号</option>{accounts.map((account) => <option value={account.id} key={account.id}>{account.account_name}</option>)}</select>
      <select aria-label="状态筛选" value={filters.status} onChange={(event) => updateFilter("status", event.target.value)}><option value="">全部状态</option>{statuses.map((value) => <option key={value}>{value}</option>)}</select>
      <select aria-label="内容类型筛选" value={filters.content_type} onChange={(event) => updateFilter("content_type", event.target.value)}><option value="">全部类型</option>{types.map((value) => <option key={value}>{value}</option>)}</select>
      <input aria-label="学科筛选" placeholder="学科" value={filters.subject} onChange={(event) => updateFilter("subject", event.target.value)} />
    </div><TableContainer><table className="data-table topic-table"><thead><tr>{["标题", "平台", "账号", "关键词数量", "目标用户", "状态", "优先级", "更新时间", "操作"].map((label) => <th key={label}>{label}</th>)}</tr></thead><tbody>{topics.map((topic) => <tr key={topic.id}><td><button className="name-button" onClick={() => setForm(topic)}>{topic.title}</button></td><td>{topic.platform}</td><td>{topic.account_name}</td><td>{topic.keyword_count}</td><td>{topic.target_user ?? "-"}</td><td><span className="status-pill">{topic.status}</span></td><td>{topic.priority}</td><td>{new Date(topic.updated_at).toLocaleDateString("zh-CN")}</td><td className="row-actions"><button onClick={() => setForm(topic)}>编辑</button><button className="danger-link" onClick={async () => { if (window.confirm("确认删除该选题？")) { await apiClient.delete(`/topics/${topic.id}`); await load(); } }}>删除</button></td></tr>)}</tbody></table></TableContainer></section>
    {form && <TopicForm value={form} accounts={accounts} keywords={keywords} onClose={() => setForm(null)} onSave={save} />}
  </>;
}

function TopicForm({ value, accounts, keywords, onClose, onSave }: { value: FormValue; accounts: Account[]; keywords: Keyword[]; onClose: () => void; onSave: (value: FormValue) => Promise<void> }) {
  const [current, setCurrent] = useState<FormValue>(value);
  const set = <K extends keyof FormValue>(key: K, next: FormValue[K]) => setCurrent((previous) => ({ ...previous, [key]: next }));
  const candidates = accounts.filter((account) => !current.platform || account.platform === current.platform);
  const submit = (event: FormEvent) => { event.preventDefault(); void onSave(current); };
  return <div className="dialog-backdrop"><section className="dialog topic-dialog"><div className="dialog-header"><h2>{current.id ? "编辑选题" : "新增选题"}</h2><button className="icon-button" onClick={onClose} aria-label="关闭">×</button></div><form className="form-grid" onSubmit={submit}>
    <label className="full-field">标题 <span>*</span><input required value={current.title} onChange={(event) => set("title", event.target.value)} /></label>
    <label>平台 <span>*</span><select required value={current.platform} onChange={(event) => { set("platform", event.target.value); set("account_id", ""); }}><option value="">请选择</option>{[...new Set(accounts.map((account) => account.platform))].map((item) => <option key={item}>{item}</option>)}</select></label>
    <label>账号 <span>*</span><select required value={current.account_id} onChange={(event) => set("account_id", event.target.value)}><option value="">请选择</option>{candidates.map((account) => <option value={account.id} key={account.id}>{account.account_name}</option>)}</select></label>
    <label>内容类型<select value={current.content_type} onChange={(event) => set("content_type", event.target.value)}>{types.map((item) => <option key={item}>{item}</option>)}</select></label>
    <label>状态<select aria-label="编辑状态" value={current.status} onChange={(event) => set("status", event.target.value)}>{statuses.map((item) => <option key={item}>{item}</option>)}</select></label>
    <label>优先级<select value={current.priority} onChange={(event) => set("priority", event.target.value)}>{priorities.map((item) => <option key={item}>{item}</option>)}</select></label>
    <label>目标用户<input value={current.target_user ?? ""} onChange={(event) => set("target_user", event.target.value)} /></label><label>学科<input value={current.subject ?? ""} onChange={(event) => set("subject", event.target.value)} /></label>
    <label className="full-field">关联关键词<select multiple aria-label="关联关键词" value={current.keyword_ids} onChange={(event) => set("keyword_ids", Array.from(event.target.selectedOptions, (option) => option.value))}>{keywords.map((keyword) => <option value={keyword.id} key={keyword.id}>{keyword.keyword}</option>)}</select></label>
    <div className="dialog-actions full-field"><button type="button" className="button secondary" onClick={onClose}>取消</button><button className="button primary">保存</button></div>
  </form></section></div>;
}
