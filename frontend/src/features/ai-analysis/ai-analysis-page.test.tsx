import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { AiAnalysisPage } from "./ai-analysis-page";

const api = vi.hoisted(() => ({ get: vi.fn(), post: vi.fn(), delete: vi.fn() }));
vi.mock("@/lib/api/client", () => ({ apiClient: api }));

const analysis = { id: "analysis-1", analysis_type: "operation", title: "运营分析", summary: "基于真实聚合数据", result_json: { key_findings: ["事实"], confidence: "中" }, provider: "deepseek", model: "deepseek-chat", prompt_version: "v1", context_version: "v1", created_at: "2026-08-14T00:00:00Z" };

describe("AiAnalysisPage", () => {
  beforeEach(() => { vi.clearAllMocks(); api.get.mockImplementation((path: string) => Promise.resolve(path.startsWith("/accounts") ? { items: [{ id: "account-1", account_name: "测试账号", platform: "小红书" }] } : { items: [analysis] })); api.post.mockResolvedValue({ ...analysis, id: "analysis-2" }); api.delete.mockResolvedValue(undefined); });
  it("loads saved analyses and creates a structured analysis", async () => { render(<AiAnalysisPage />); await screen.findByText("运营分析"); fireEvent.click(screen.getByRole("button", { name: "开始分析" })); await waitFor(() => expect(api.post).toHaveBeenCalledWith("/ai/analysis", expect.objectContaining({ analysis_type: "operation" }))); await screen.findByText("关键发现"); });
});
