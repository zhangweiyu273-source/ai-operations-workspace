import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import ReviewsPage from "./page";

const api = vi.hoisted(() => ({ get: vi.fn(), post: vi.fn(), put: vi.fn(), delete: vi.fn() }));
vi.mock("@/lib/api/client", () => ({ apiClient: api }));
const review = { id: "r1", task_id: "t1", title: "发布复盘", review_date: "2026-08-14", result: "完成", updated_at: "2026-08-14T00:00:00Z" };

describe("ReviewsPage", () => {
  beforeEach(() => { vi.clearAllMocks(); api.get.mockImplementation((path: string) => path.startsWith("/reviews") ? Promise.resolve({ items: [review], total: 21, page: 1, page_size: 20, total_pages: 2 }) : Promise.resolve({ items: [{ id: "t1", title: "发布任务" }] })); api.post.mockResolvedValue(review); api.put.mockResolvedValue(review); api.delete.mockResolvedValue(undefined); vi.spyOn(window, "confirm").mockReturnValue(true); });
  it("loads, paginates, creates, edits, searches and deletes reviews", async () => { render(<ReviewsPage/>); await screen.findByText("发布复盘"); fireEvent.change(screen.getByLabelText("搜索复盘"), { target: { value: "发布" } }); await waitFor(() => expect(api.get).toHaveBeenCalledWith(expect.stringContaining("search=%E5%8F%91%E5%B8%83"))); fireEvent.click(screen.getByRole("button", { name: "下一页" })); await waitFor(() => expect(api.get).toHaveBeenCalledWith(expect.stringContaining("page=2"))); fireEvent.click(screen.getByRole("button", { name: "新建复盘" })); fireEvent.change(screen.getByLabelText("关联任务"), { target: { value: "t1" } }); fireEvent.change(screen.getByLabelText("标题 *"), { target: { value: "新复盘" } }); fireEvent.click(screen.getByRole("button", { name: "保存" })); await waitFor(() => expect(api.post).toHaveBeenCalledWith("/reviews", expect.objectContaining({ task_id: "t1", title: "新复盘" }))); fireEvent.click(screen.getByRole("button", { name: "编辑" })); fireEvent.click(screen.getByRole("button", { name: "保存" })); await waitFor(() => expect(api.put).toHaveBeenCalledWith("/reviews/r1", expect.any(Object))); fireEvent.click(screen.getByRole("button", { name: "删除" })); await waitFor(() => expect(api.delete).toHaveBeenCalledWith("/reviews/r1")); });
});
