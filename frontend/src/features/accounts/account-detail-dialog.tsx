import type { Account } from "./types";

const date = (value: string) => new Intl.DateTimeFormat("zh-CN", { dateStyle: "medium", timeStyle: "short" }).format(new Date(value));

export function AccountDetailDialog({ account, onClose }: { account: Account; onClose: () => void }) {
  const fields = [
    ["账号名称", account.account_name], ["平台", account.platform], ["账号类型", account.account_type],
    ["状态", account.status], ["负责人", account.operator], ["账号定位", account.positioning],
    ["目标用户", account.target_user], ["创建时间", date(account.created_at)], ["更新时间", date(account.updated_at)],
  ];
  return <div className="dialog-backdrop" role="presentation"><section className="dialog" role="dialog" aria-modal="true" aria-labelledby="account-detail-title"><div className="dialog-header"><h2 id="account-detail-title">账号详情</h2><button className="icon-button" onClick={onClose} aria-label="关闭">×</button></div><dl className="detail-grid">{fields.map(([label, value]) => <div key={label}><dt>{label}</dt><dd>{value || "—"}</dd></div>)}</dl>{account.account_url ? <a className="text-link" href={account.account_url} target="_blank" rel="noreferrer">打开账号链接</a> : null}<div className="reserved-data"><strong>数据概览</strong><p>内容数据、粉丝数据和线索数据将在后续阶段接入。</p></div><div className="dialog-actions"><button className="button secondary" onClick={onClose}>关闭</button></div></section></div>;
}
