"use client";

import { FormEvent, useCallback, useEffect, useState } from "react";
import { PageHeader } from "@/components/ui/page-header";
import { TableContainer } from "@/components/ui/table-container";
import { apiClient } from "@/lib/api/client";

type Task = { id: string; title: string };
type Review = { id: string; task_id: string; title: string; review_date: string; goal?: string; result?: string; problem?: string; improvement?: string; next_action?: string; updated_at: string };
type FormValue = Omit<Review, "id" | "updated_at"> & { id?: string };
type ReviewList = { items: Review[]; total: number; page: number; page_size: number; total_pages: number };
const blank = (): FormValue => ({ task_id: "", title: "", review_date: new Date().toISOString().slice(0, 10), goal: "", result: "", problem: "", improvement: "", next_action: "" });

export default function ReviewsPage() {
  const [data, setData] = useState<ReviewList | null>(null); const [tasks, setTasks] = useState<Task[]>([]); const [form, setForm] = useState<FormValue | null>(null); const [search, setSearch] = useState(""); const [page, setPage] = useState(1); const [error, setError] = useState("");
  const load = useCallback(async () => {
    const query = new URLSearchParams({ page: String(page), page_size: "20" }); if (search) query.set("search", search);
    const [reviews, taskData] = await Promise.all([apiClient.get<ReviewList>(`/reviews?${query}`), apiClient.get<{ items: Task[] }>("/tasks?page_size=100")]);
    setData(reviews); setTasks(taskData.items);
  }, [page, search]);
  useEffect(() => { const timer = window.setTimeout(() => { void load().catch(() => setError("复盘数据加载失败")); }, 0); return () => window.clearTimeout(timer); }, [load]);
  async function save(value: FormValue) { if (!value.title.trim() || !value.task_id) { setError("请填写标题并选择关联任务"); return; } try { if (value.id) await apiClient.put(`/reviews/${value.id}`, value); else await apiClient.post("/reviews", value); setForm(null); setError(""); await load(); } catch { setError("复盘保存失败"); } }
  async function remove(review: Review) { if (!window.confirm(`确认删除复盘“${review.title}”吗？`)) return; try { await apiClient.delete(`/reviews/${review.id}`); await load(); } catch { setError("复盘删除失败"); } }
  const totalPages = Math.max(data?.total_pages ?? 0, 1);
  return <><PageHeader title="运营复盘" description="记录目标、结果、问题与下一步行动。" actions={<button className="button primary" onClick={() => setForm(blank())}>新建复盘</button>} />{error && <p role="alert" className="error-message">{error}</p>}<section className="account-list-card"><div className="filter-bar"><input aria-label="搜索复盘" value={search} placeholder="搜索标题、结果或问题" onChange={(e) => { setPage(1); setSearch(e.target.value); }} /></div><TableContainer><table className="data-table"><thead><tr><th>标题</th><th>关联任务</th><th>日期</th><th>结果</th><th>问题</th><th>操作</th></tr></thead><tbody>{data?.items.map((item) => <tr key={item.id}><td>{item.title}</td><td>{tasks.find((task) => task.id === item.task_id)?.title || item.task_id}</td><td>{item.review_date}</td><td>{item.result || "-"}</td><td>{item.problem || "-"}</td><td className="row-actions"><button onClick={() => setForm(item)}>编辑</button><button className="danger-link" onClick={() => void remove(item)}>删除</button></td></tr>)}</tbody></table></TableContainer><div className="pagination" aria-label="复盘分页"><span>共 {data?.total ?? 0} 条</span><button className="button secondary" disabled={page <= 1} onClick={() => setPage((current) => current - 1)}>上一页</button><span>{page} / {totalPages}</span><button className="button secondary" disabled={page >= totalPages} onClick={() => setPage((current) => current + 1)}>下一页</button></div></section>{form && <ReviewForm value={form} tasks={tasks} onClose={() => setForm(null)} onSave={save} />}</>;
}

function ReviewForm({ value, tasks, onClose, onSave }: { value: FormValue; tasks: Task[]; onClose: () => void; onSave: (v: FormValue) => Promise<void> }) {
  const [current, setCurrent] = useState(value); const submit = (e: FormEvent) => { e.preventDefault(); void onSave(current); };
  return <div className="dialog-backdrop"><section className="dialog"><div className="dialog-header"><h2>{current.id ? "编辑复盘" : "新建复盘"}</h2><button aria-label="关闭" onClick={onClose}>×</button></div><form className="form-grid" onSubmit={submit}><label>关联任务 *<select aria-label="关联任务" required value={current.task_id} onChange={(e) => setCurrent({ ...current, task_id: e.target.value })}><option value="">请选择</option>{tasks.map((v) => <option value={v.id} key={v.id}>{v.title}</option>)}</select></label><label>复盘日期<input type="date" value={current.review_date} onChange={(e) => setCurrent({ ...current, review_date: e.target.value })} /></label><label className="full-field">标题 *<input required value={current.title} onChange={(e) => setCurrent({ ...current, title: e.target.value })} /></label>{(["goal", "result", "problem", "improvement", "next_action"] as const).map((name) => <label className="full-field" key={name}>{({ goal: "目标", result: "结果", problem: "问题", improvement: "改进方案", next_action: "下一步行动" }[name])}<textarea value={current[name] || ""} onChange={(e) => setCurrent({ ...current, [name]: e.target.value })} /></label>)}<div className="dialog-actions full-field"><button type="button" className="button secondary" onClick={onClose}>取消</button><button className="button primary">保存</button></div></form></section></div>;
}
