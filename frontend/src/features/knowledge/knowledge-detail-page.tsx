"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { ErrorState } from "@/components/ui/error-state";
import { LoadingState } from "@/components/ui/loading-state";
import { PageHeader } from "@/components/ui/page-header";
import { apiClient } from "@/lib/api/client";
import { extractKnowledgeEntries } from "./knowledge-entry-parser";

type Knowledge = { id:string; title:string; category:string; content:string; summary?:string; source_type?:string; source_name?:string; priority:string; status:string; tags:string[]; created_at:string; updated_at:string };

export function KnowledgeDetailPage({id}:{id:string}) {
  const [item,setItem] = useState<Knowledge|null>(null);
  const [error,setError] = useState("");
  useEffect(() => { void apiClient.get<Knowledge>(`/knowledge/${id}`).then(setItem).catch(() => setError("知识详情加载失败")); },[id]);
  if (error) return <ErrorState message={error} />;
  if (!item) return <LoadingState label="正在加载知识详情…" />;
  const entries = extractKnowledgeEntries(item.content);
  return <>
    <PageHeader title={item.title} description="知识文档详情与词条解释。" actions={<Link className="button secondary" href="/knowledge">返回知识库</Link>} />
    <section className="knowledge-detail-card">
      <dl className="detail-grid"><div><dt>分类</dt><dd>{item.category}</dd></div><div><dt>优先级</dt><dd>{item.priority}</dd></div><div><dt>标签</dt><dd>{item.tags.join("、") || "-"}</dd></div><div><dt>更新时间</dt><dd>{new Date(item.updated_at).toLocaleString("zh-CN")}</dd></div></dl>
      {item.summary && <section className="knowledge-summary"><h2>摘要</h2><p>{item.summary}</p></section>}
      <section className="knowledge-entry-list"><h2>词条与解释</h2>{entries.map((entry) => <article className="knowledge-entry" key={entry.term}><h3>{entry.term}</h3><p>{entry.explanation}</p></article>)}</section>
      <section className="knowledge-source"><h2>完整正文</h2><pre>{item.content}</pre></section>
    </section>
  </>;
}
