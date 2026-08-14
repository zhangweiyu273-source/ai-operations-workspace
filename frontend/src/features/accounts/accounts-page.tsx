"use client";

import { useCallback, useEffect, useState } from "react";
import { ErrorState } from "@/components/ui/error-state";
import { LoadingState } from "@/components/ui/loading-state";
import { PageHeader } from "@/components/ui/page-header";
import { TableContainer } from "@/components/ui/table-container";
import { createAccount, deleteAccount, listAccounts, updateAccount } from "./api";
import { AccountDetailDialog } from "./account-detail-dialog";
import { AccountFormDialog } from "./account-form-dialog";
import { emptyAccount, type Account, type AccountList, type AccountWrite } from "./types";

export function AccountsPage() {
  const [data, setData] = useState<AccountList | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchInput, setSearchInput] = useState("");
  const [filters, setFilters] = useState({ search: "", platform: "", accountType: "", status: "" });
  const [page, setPage] = useState(1);
  const [formAccount, setFormAccount] = useState<Account | "create" | null>(null);
  const [detail, setDetail] = useState<Account | null>(null);
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true); setError(null);
    try { setData(await listAccounts({ ...filters, page, pageSize: 10 })); }
    catch (reason) { setError(reason instanceof Error ? reason.message : "账号数据加载失败"); }
    finally { setLoading(false); }
  }, [filters, page]);
  useEffect(() => {
    const timer = window.setTimeout(() => void load(), 0);
    return () => window.clearTimeout(timer);
  }, [load]);

  async function save(value: AccountWrite) {
    setSaving(true); setFormError(null);
    try {
      if (formAccount === "create") await createAccount(value);
      else if (formAccount) await updateAccount(formAccount.id, value);
      setFormAccount(null); await load();
    } catch (reason) { setFormError(reason instanceof Error ? reason.message : "保存失败"); }
    finally { setSaving(false); }
  }
  async function remove(account: Account) {
    if (!window.confirm(`确认删除账号“${account.account_name}”吗？删除后列表将不再显示。`)) return;
    try { await deleteAccount(account.id); await load(); }
    catch (reason) { setError(reason instanceof Error ? reason.message : "删除失败"); }
  }
  function applySearch() { setPage(1); setFilters((current) => ({ ...current, search: searchInput.trim() })); }

  return <>
    <PageHeader title="账号矩阵" description="统一管理企业公域账号。" actions={<button className="button primary" onClick={() => setFormAccount("create")}>新增账号</button>} />
    <div className="metric-grid" aria-label="账号统计"><div className="metric-card"><span>账号数量</span><strong>{data?.summary.account_count ?? "—"}</strong></div><div className="metric-card"><span>平台数量</span><strong>{data?.summary.platform_count ?? "—"}</strong></div><div className="metric-card"><span>启用账号</span><strong>{data?.summary.active_count ?? "—"}</strong></div></div>
    <section className="account-list-card">
      <div className="filter-bar"><form onSubmit={(event) => { event.preventDefault(); applySearch(); }}><input aria-label="搜索账号" placeholder="搜索账号名称、定位、目标用户" value={searchInput} onChange={(e) => setSearchInput(e.target.value)} /><button className="button secondary">搜索</button></form><select aria-label="平台筛选" value={filters.platform} onChange={(e) => { setPage(1); setFilters({ ...filters, platform: e.target.value }); }}><option value="">全部平台</option><option>小红书</option><option>抖音</option><option>视频号</option><option>公众号</option><option>其他</option></select><select aria-label="类型筛选" value={filters.accountType} onChange={(e) => { setPage(1); setFilters({ ...filters, accountType: e.target.value }); }}><option value="">全部类型</option><option>老板IP</option><option>品牌账号</option><option>老师IP</option><option>矩阵账号</option></select><select aria-label="状态筛选" value={filters.status} onChange={(e) => { setPage(1); setFilters({ ...filters, status: e.target.value }); }}><option value="">全部状态</option><option>启用</option><option>停用</option><option>测试中</option></select></div>
      {loading ? <LoadingState label="正在加载账号…" /> : error ? <ErrorState message={error} /> : data?.items.length ? <><TableContainer><table className="data-table"><thead><tr><th>账号名称</th><th>平台</th><th>类型</th><th>定位</th><th>目标用户</th><th>负责人</th><th>状态</th><th>更新时间</th><th>操作</th></tr></thead><tbody>{data.items.map((account) => <tr key={account.id}><td><button className="name-button" onClick={() => setDetail(account)}>{account.account_name}</button></td><td>{account.platform}</td><td>{account.account_type}</td><td>{account.positioning || "—"}</td><td>{account.target_user || "—"}</td><td>{account.operator || "—"}</td><td><span className={`status-pill status-${account.status}`}>{account.status}</span></td><td>{new Date(account.updated_at).toLocaleDateString("zh-CN")}</td><td><div className="row-actions"><button onClick={() => setDetail(account)}>查看</button><button onClick={() => setFormAccount(account)}>编辑</button><button className="danger-link" onClick={() => void remove(account)}>删除</button></div></td></tr>)}</tbody></table></TableContainer><div className="pagination"><span>共 {data.total} 条</span><button className="button secondary" disabled={page <= 1} onClick={() => setPage(page - 1)}>上一页</button><span>{page} / {Math.max(data.total_pages, 1)}</span><button className="button secondary" disabled={page >= data.total_pages} onClick={() => setPage(page + 1)}>下一页</button></div></> : <div className="account-empty"><strong>暂无账号</strong><p>点击“新增账号”建立第一个公域账号档案。</p></div>}
    </section>
    {formAccount ? <AccountFormDialog key={formAccount === "create" ? "create" : formAccount.id} mode={formAccount === "create" ? "create" : "edit"} initial={formAccount === "create" ? emptyAccount : formAccount} busy={saving} error={formError} onClose={() => { setFormAccount(null); setFormError(null); }} onSubmit={save} /> : null}
    {detail ? <AccountDetailDialog account={detail} onClose={() => setDetail(null)} /> : null}
  </>;
}
