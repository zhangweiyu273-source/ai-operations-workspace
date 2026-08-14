import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import Home from "./page";

const api = vi.hoisted(() => ({ get: vi.fn() }));
vi.mock("@/lib/api/client", () => ({ apiClient: api }));

const dashboard = { tasks: { today: 2, in_progress: 1, overdue: 1, pending_review: 1 }, content: { total: 4, pending_creation: 1, in_production: 1, published: 2 }, keywords: { total: 6, high_commercial_intent: 2, unused: 3, recently_added: 1 }, accounts: { total: 2, platform_distribution: { 小红书: 1, 抖音: 1 }, recently_updated: { id: "a1", account_name: "数学账号", platform: "小红书", updated_at: "2026-08-14T00:00:00Z" } }, knowledge: { total: 3, category_count: 2, recently_updated: { id: "k1", title: "课程资料", category: "课程资料", updated_at: "2026-08-14T00:00:00Z" } }, today_tasks: [{ id: "t1", title: "制作数学视频", task_type: "内容创作", account_name: "数学账号", topic_title: "数学选题", priority: "高", status: "进行中", deadline: null, is_overdue: false }], review_reminders: [{ id: "r1", title: "发布复盘", task_title: "制作数学视频", review_date: "2026-08-14", problem_summary: "互动率偏低" }] };

describe("Home dashboard", () => {
  beforeEach(() => { vi.clearAllMocks(); api.get.mockResolvedValue(dashboard); });
  it("loads all dashboard modules from one API and refreshes", async () => {
    render(<Home />); await screen.findByRole("heading", { name: "运营首页" });
    expect(api.get).toHaveBeenCalledTimes(1); expect(api.get).toHaveBeenCalledWith("/dashboard");
    expect(screen.getAllByText("今日任务")).toHaveLength(2); expect(screen.getByText("关键词资产")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /内容创作.*数学选题/ })).toHaveAttribute("href", "/tasks?taskId=t1");
    fireEvent.click(screen.getByRole("button", { name: "刷新数据" })); await waitFor(() => expect(api.get).toHaveBeenCalledTimes(2));
  });
});
