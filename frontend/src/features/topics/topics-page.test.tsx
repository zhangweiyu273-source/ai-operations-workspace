import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { TopicsPage } from "./topics-page";

const api = vi.hoisted(() => ({ get: vi.fn(), post: vi.fn(), put: vi.fn(), delete: vi.fn() }));
vi.mock("@/lib/api/client", () => ({ apiClient: api }));
const account = { id: "a1", account_name: "小红书账号", platform: "小红书" };
const keyword1 = { id: "k1", keyword: "初三数学提分" };
const keyword2 = { id: "k2", keyword: "广州数学补课" };
const topic = { id: "t1", title: "数学50分怎么办", platform: "小红书", account_id: "a1", account_name: "小红书账号", content_type: "图文", status: "待创作", priority: "高", subject: "数学", target_user: "初三家长", keyword_count: 2, keyword_ids: ["k1", "k2"], updated_at: "2026-08-14T00:00:00Z" };

describe("TopicsPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    api.get.mockImplementation((path: string) => {
      if (path.startsWith("/accounts")) return Promise.resolve({ items: [account] });
      if (path.startsWith("/keywords")) return Promise.resolve({ items: [keyword1, keyword2] });
      if (path.startsWith("/topics/stats")) return Promise.resolve({ total: 1, pending_creation: 1, in_production: 0, published: 0, reviewed: 0 });
      return Promise.resolve({ items: [topic] });
    });
    api.post.mockResolvedValue(topic); api.put.mockResolvedValue(topic); api.delete.mockResolvedValue(undefined);
  });
  it("loads topic statistics and applies search and all primary filters", async () => {
    render(<TopicsPage />); await screen.findByRole("button", { name: topic.title });
    for (const [label, value] of [["搜索选题", "数学"], ["平台筛选", "小红书"], ["账号筛选", "a1"], ["状态筛选", "待创作"], ["内容类型筛选", "图文"], ["学科筛选", "数学"]] as const) {
      fireEvent.change(screen.getByLabelText(label), { target: { value } });
    }
    await waitFor(() => expect(api.get).toHaveBeenLastCalledWith(expect.stringContaining("subject=%E6%95%B0%E5%AD%A6")));
    expect(screen.getByText("选题总数")).toBeInTheDocument();
  });
  it("creates with multiple keywords, edits status, validates required fields, and deletes", async () => {
    vi.spyOn(window, "confirm").mockReturnValue(true); render(<TopicsPage />); await screen.findByRole("button", { name: topic.title });
    fireEvent.click(screen.getByRole("button", { name: "新增选题" }));
    fireEvent.click(screen.getByRole("button", { name: "保存" }));
    expect(api.post).not.toHaveBeenCalled();
    fireEvent.change(screen.getByLabelText("标题 *"), { target: { value: "新选题" } });
    fireEvent.change(screen.getByLabelText("平台 *"), { target: { value: "小红书" } });
    fireEvent.change(screen.getByLabelText("账号 *"), { target: { value: "a1" } });
    const multi = screen.getByLabelText("关联关键词") as HTMLSelectElement;
    for (const option of Array.from(multi.options)) option.selected = true;
    fireEvent.change(multi);
    fireEvent.click(screen.getByRole("button", { name: "保存" }));
    await waitFor(() => expect(api.post).toHaveBeenCalledWith("/topics", expect.objectContaining({ title: "新选题", keyword_ids: ["k1", "k2"] })));
    fireEvent.click(screen.getByRole("button", { name: topic.title }));
    fireEvent.change(screen.getByLabelText("编辑状态"), { target: { value: "已发布" } }); fireEvent.click(screen.getByRole("button", { name: "保存" }));
    await waitFor(() => expect(api.put).toHaveBeenCalledWith("/topics/t1", expect.objectContaining({ status: "已发布" })));
    fireEvent.click(screen.getByRole("button", { name: "删除" })); await waitFor(() => expect(api.delete).toHaveBeenCalledWith("/topics/t1"));
  });
});
