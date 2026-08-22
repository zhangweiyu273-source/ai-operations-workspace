"use client";

import Link from "next/link";
import { FormEvent, useCallback, useEffect, useState } from "react";
import { EmptyState } from "@/components/ui/empty-state";
import { ErrorState } from "@/components/ui/error-state";
import { LoadingState } from "@/components/ui/loading-state";
import { PageHeader } from "@/components/ui/page-header";
import { TableContainer } from "@/components/ui/table-container";
import { apiClient } from "@/lib/api/client";
import { findMatchingKnowledgeEntries } from "./knowledge-entry-parser";

type Item = { id:string; title:string; category:string; content:string; summary?:string; source_type?:string; source_name?:string; priority:string; status:string; tags:string[]; updated_at:string };
type Stats = { total:number; category_count:number; high_priority:number; recently_updated:number };
type FormItem = Omit<Item,"id"|"updated_at"> & { id?:string; tag_text?:string };
type Filters = { search:string; category:string; status:string; priority:string; tag:string };

const empty = (): Omit<Item,"id"|"updated_at"> => ({ title:"", category:"", content:"", priority:"中", status:"启用", tags:[] });

export function KnowledgePage() {
  const [items,setItems] = useState<Item[]>([]);
  const [categories,setCategories] = useState<string[]>([]);
  const [tags,setTags] = useState<string[]>([]);
  const [stats,setStats] = useState<Stats|null>(null);
  const [form,setForm] = useState<FormItem|null>(null);
  const [filters,setFilters] = useState<Filters>({ search:"", category:"", status:"", priority:"", tag:"" });
  const [searchInput,setSearchInput] = useState("");
  const [loading,setLoading] = useState(true);
  const [error,setError] = useState("");

  const load = useCallback(async () => {
    setLoading(true); setError("");
    try {
      const query = new URLSearchParams({ page:"1", page_size:"20" });
      Object.entries(filters).forEach(([key,value]) => value && query.set(key,value));
      const [list,categoryOptions,tagOptions,summary] = await Promise.all([
        apiClient.get<{items:Item[]}>(`/knowledge?${query}`),
        apiClient.get<{items:string[]}>("/knowledge/categories"),
        apiClient.get<{items:string[]}>("/knowledge/tags"),
        apiClient.get<Stats>("/knowledge/stats"),
      ]);
      setItems(list.items); setCategories(categoryOptions.items); setTags(tagOptions.items); setStats(summary);
    } catch { setError("知识库加载失败"); }
    finally { setLoading(false); }
  },[filters]);

  useEffect(() => {
    const timer = window.setTimeout(() => void load(), 0);
    return () => window.clearTimeout(timer);
  },[load]);
  const applySearch = () => setFilters((current) => ({ ...current, search:searchInput.trim() }));
  const clearSearch = () => { setSearchInput(""); setFilters((current) => ({ ...current, search:"" })); };

  async function save(value:FormItem) {
    if (!value.title.trim() || !value.content.trim() || !value.category) { setError("请填写标题、分类和正文。"); return; }
    if (value.id) await apiClient.put(`/knowledge/${value.id}`,value); else await apiClient.post("/knowledge",value);
    setForm(null); await load();
  }
  async function remove(item:Item) { if (!confirm("确认删除该知识？")) return; await apiClient.delete(`/knowledge/${item.id}`); await load(); }

  return <>
    <PageHeader title="知识库" description="沉淀公司、课程、销售与运营知识资产。" actions={<button className="button primary" onClick={() => setForm(empty())}>新增知识</button>} />
    {error && <p role="alert" className="error-message">{error}</p>}
    <section className="stat-grid">{[["知识总量",stats?.total],["分类数量",stats?.category_count],["高优先级",stats?.high_priority],["最近更新",stats?.recently_updated]].map(([label,value]) => <div className="stat-card" key={String(label)}><span>{label}</span><strong>{value ?? "-"}</strong></div>)}</section>
    <section className="account-list-card">
      <div className="filter-bar">
        <form onSubmit={(event) => { event.preventDefault(); applySearch(); }}>
          <input aria-label="搜索知识" value={searchInput} placeholder="搜索标题、正文或摘要" onChange={(event) => setSearchInput(event.target.value)} onKeyDown={(event) => { if (event.key === "Enter") { event.preventDefault(); applySearch(); } }} />
          <button className="button secondary" type="submit" disabled={loading}>搜索</button>
          {(searchInput || filters.search) && <button className="button secondary" type="button" onClick={clearSearch} disabled={loading}>清空</button>}
        </form>
        <select aria-label="分类筛选" value={filters.category} onChange={(event) => setFilters({ ...filters, category:event.target.value })}><option value="">全部分类</option>{categories.map((value) => <option key={value}>{value}</option>)}</select>
        <select aria-label="状态筛选" value={filters.status} onChange={(event) => setFilters({ ...filters, status:event.target.value })}><option value="">全部状态</option>{["启用","停用","草稿"].map((value) => <option key={value}>{value}</option>)}</select>
        <select aria-label="优先级筛选" value={filters.priority} onChange={(event) => setFilters({ ...filters, priority:event.target.value })}><option value="">全部优先级</option>{["高","中","低"].map((value) => <option key={value}>{value}</option>)}</select>
        <select aria-label="标签筛选" value={filters.tag} onChange={(event) => setFilters({ ...filters, tag:event.target.value })}><option value="">全部标签</option>{tags.map((value) => <option key={value}>{value}</option>)}</select>
      </div>
      {loading ? <LoadingState label="正在搜索知识库…" /> : error ? <ErrorState message={error} /> : items.length ? <KnowledgeTable items={items} search={filters.search} onEdit={setForm} onDelete={remove} /> : <EmptyState title={filters.search ? "未找到匹配知识" : "暂无知识"} description={filters.search ? "请尝试其他关键词，或清空搜索恢复完整列表。" : "可通过“新增知识”沉淀知识资产。"} />}
    </section>
    {form && <Form value={form} categories={categories} onClose={() => setForm(null)} onSave={save} />}
  </>;
}

function KnowledgeTable({items,search,onEdit,onDelete}:{items:Item[]; search:string; onEdit:(item:Item) => void; onDelete:(item:Item) => Promise<void>}) {
  return <TableContainer><table className="data-table knowledge-table"><thead><tr>{["标题 / 命中词条","分类","标签","优先级","状态","更新时间","操作"].map((value) => <th key={value}>{value}</th>)}</tr></thead><tbody>{items.map((item) => {
    const matches = findMatchingKnowledgeEntries(item.content,search);
    return <tr key={item.id}><td><Link className="knowledge-title-link" href={`/knowledge/${item.id}`}>{item.title}</Link>{search && matches.map((entry) => <div className="knowledge-match" key={entry.term}><strong>词条：{entry.term}</strong><p>解释：{entry.explanation}</p></div>)}</td><td>{item.category}</td><td>{item.tags.join("、") || "-"}</td><td>{item.priority}</td><td>{item.status}</td><td>{new Date(item.updated_at).toLocaleDateString("zh-CN")}</td><td className="row-actions"><Link href={`/knowledge/${item.id}`}>查看详情</Link><button onClick={() => onEdit(item)}>编辑</button><button className="danger-link" onClick={() => void onDelete(item)}>删除</button></td></tr>;
  })}</tbody></table></TableContainer>;
}

function Form({value,categories,onClose,onSave}:{value:FormItem; categories:string[]; onClose:() => void; onSave:(value:FormItem) => Promise<void>}) {
  const [formValue,setFormValue] = useState(value);
  const submit = (event:FormEvent) => { event.preventDefault(); void onSave({ ...formValue, tags:(formValue.tag_text || "").split(",").map((tag) => tag.trim()).filter(Boolean) }); };
  return <div className="dialog-backdrop"><section className="dialog"><div className="dialog-header"><h2>{formValue.id ? "编辑知识" : "新增知识"}</h2><button onClick={onClose} aria-label="关闭">×</button></div><form className="form-grid" onSubmit={submit}><label className="full-field">标题 *<input required value={formValue.title} onChange={(event) => setFormValue({ ...formValue, title:event.target.value })} /></label><label>分类 *<select required value={formValue.category} onChange={(event) => setFormValue({ ...formValue, category:event.target.value })}><option value="">请选择</option>{categories.map((category) => <option key={category}>{category}</option>)}</select></label><label>优先级<select value={formValue.priority} onChange={(event) => setFormValue({ ...formValue, priority:event.target.value })}>{["高","中","低"].map((priority) => <option key={priority}>{priority}</option>)}</select></label><label>状态<select value={formValue.status} onChange={(event) => setFormValue({ ...formValue, status:event.target.value })}>{["启用","停用","草稿"].map((status) => <option key={status}>{status}</option>)}</select></label><label>来源<input value={formValue.source_type || ""} onChange={(event) => setFormValue({ ...formValue, source_type:event.target.value })} /></label><label className="full-field">标签（逗号分隔）<input aria-label="标签" defaultValue={(formValue.tags || []).join(",")} onChange={(event) => setFormValue({ ...formValue, tag_text:event.target.value })} /></label><label className="full-field">摘要<textarea value={formValue.summary || ""} onChange={(event) => setFormValue({ ...formValue, summary:event.target.value })} /></label><label className="full-field">正文 *<textarea required aria-label="正文" value={formValue.content} onChange={(event) => setFormValue({ ...formValue, content:event.target.value })} /></label><div className="dialog-actions full-field"><button type="button" className="button secondary" onClick={onClose}>取消</button><button className="button primary">保存</button></div></form></section></div>;
}
