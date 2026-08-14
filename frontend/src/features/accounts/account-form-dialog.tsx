"use client";

import { FormEvent, useState } from "react";
import type { AccountWrite } from "./types";

const platforms = ["小红书", "抖音", "视频号", "公众号", "其他"];
const accountTypes = ["老板IP", "品牌账号", "老师IP", "矩阵账号"];

export function AccountFormDialog({
  initial,
  mode,
  busy,
  error,
  onClose,
  onSubmit,
}: {
  initial: AccountWrite;
  mode: "create" | "edit";
  busy: boolean;
  error: string | null;
  onClose: () => void;
  onSubmit: (data: AccountWrite) => Promise<void>;
}) {
  const [form, setForm] = useState(initial);
  const [validation, setValidation] = useState<string | null>(null);
  const set = (key: keyof AccountWrite, value: string) =>
    setForm((current) => ({ ...current, [key]: value || null }));

  async function submit(event: FormEvent) {
    event.preventDefault();
    if (!form.account_name.trim() || !form.platform || !form.account_type) {
      setValidation("请填写账号名称、平台和账号类型");
      return;
    }
    setValidation(null);
    await onSubmit({ ...form, account_name: form.account_name.trim() });
  }

  return (
    <div className="dialog-backdrop" role="presentation">
      <section className="dialog" role="dialog" aria-modal="true" aria-labelledby="account-form-title">
        <div className="dialog-header">
          <h2 id="account-form-title">{mode === "create" ? "新增账号" : "编辑账号"}</h2>
          <button className="icon-button" type="button" onClick={onClose} aria-label="关闭">×</button>
        </div>
        <form onSubmit={submit}>
          <div className="form-grid">
            <label>账号名称<span>*</span><input value={form.account_name} onChange={(e) => set("account_name", e.target.value)} /></label>
            <label>平台<span>*</span><select value={form.platform} onChange={(e) => set("platform", e.target.value)}>{platforms.map((item) => <option key={item}>{item}</option>)}</select></label>
            <label>账号类型<span>*</span><select value={form.account_type} onChange={(e) => set("account_type", e.target.value)}>{accountTypes.map((item) => <option key={item}>{item}</option>)}</select></label>
            <label>状态<select value={form.status} onChange={(e) => set("status", e.target.value)}><option>启用</option><option>停用</option><option>测试中</option></select></label>
            <label className="full-field">账号链接<input type="url" value={form.account_url ?? ""} onChange={(e) => set("account_url", e.target.value)} placeholder="https://" /></label>
            <label>账号定位<input value={form.positioning ?? ""} onChange={(e) => set("positioning", e.target.value)} /></label>
            <label>目标用户<input value={form.target_user ?? ""} onChange={(e) => set("target_user", e.target.value)} /></label>
            <label>负责人<input value={form.operator ?? ""} onChange={(e) => set("operator", e.target.value)} /></label>
            <label className="full-field">备注<textarea rows={3} value={form.description ?? ""} onChange={(e) => set("description", e.target.value)} /></label>
          </div>
          {validation || error ? <p className="form-error" role="alert">{validation ?? error}</p> : null}
          <div className="dialog-actions"><button className="button secondary" type="button" onClick={onClose}>取消</button><button className="button primary" disabled={busy}>{busy ? "保存中…" : "保存"}</button></div>
        </form>
      </section>
    </div>
  );
}
