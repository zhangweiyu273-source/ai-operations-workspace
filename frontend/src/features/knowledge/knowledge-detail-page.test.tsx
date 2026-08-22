import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { KnowledgeDetailPage } from "./knowledge-detail-page";

const api = vi.hoisted(() => ({ get: vi.fn() }));
vi.mock("@/lib/api/client", () => ({ apiClient: api }));

describe("KnowledgeDetailPage", () => {
  it("shows every XSC, MK and HD glossary explanation", async () => {
    api.get.mockResolvedValue({
      id: "k1",
      title: "广州小升初XSC完整黑话词典",
      category: "行业资料",
      content: "### XSC\n**含义：** 小升初（小学升初中）的拼音首字母。\n\n### MK\n**含义：** 密考，家长圈对非公开测试的称呼。\n\n### HD\n**含义：** 活动，家长圈对体验或交流活动的称呼。",
      priority: "高",
      status: "启用",
      tags: ["广州", "XSC"],
      created_at: "2026-08-22T00:00:00Z",
      updated_at: "2026-08-22T00:00:00Z",
    });

    render(<KnowledgeDetailPage id="k1" />);

    expect(await screen.findByRole("heading", { name: "XSC" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "MK" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "HD" })).toBeInTheDocument();
    expect(screen.getByText("密考，家长圈对非公开测试的称呼。")).toBeInTheDocument();
    expect(api.get).toHaveBeenCalledWith("/knowledge/k1");
  });
});
