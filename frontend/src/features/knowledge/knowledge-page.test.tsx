import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { KnowledgePage } from "./knowledge-page";

const api = vi.hoisted(() => ({ get: vi.fn(), post: vi.fn(), put: vi.fn(), delete: vi.fn() }));
vi.mock("@/lib/api/client", () => ({ apiClient: api }));

const item = { id:"k1", title:"广州小升初XSC完整黑话词典", category:"行业资料", content:"### XSC\n**含义：** 小升初（小学升初中）的拼音首字母。\n\n### MK\n**含义：** 密考，家长圈对非公开测试的称呼。\n\n### HD\n**含义：** 活动，家长圈对体验或交流活动的称呼。", summary:"广州小升初术语", priority:"高", status:"启用", tags:["XSC","家长圈"], updated_at:"2026-08-14T00:00:00Z" };

describe("KnowledgePage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    api.get.mockImplementation((path:string) => path.startsWith("/knowledge/categories") ? Promise.resolve({ items:["课程资料","行业资料"] }) : path.startsWith("/knowledge/tags") ? Promise.resolve({ items:["数学","家长"] }) : path.startsWith("/knowledge/stats") ? Promise.resolve({ total:1, category_count:1, high_priority:1, recently_updated:1 }) : Promise.resolve({ items:[item] }));
    api.post.mockResolvedValue(item); api.put.mockResolvedValue(item); api.delete.mockResolvedValue(undefined);
  });

  it("shows matched XSC, MK and HD entries through the search button and Enter", async () => {
    render(<KnowledgePage />);
    await screen.findByRole("link", { name:"广州小升初XSC完整黑话词典" });
    const input = screen.getByLabelText("搜索知识");

    fireEvent.change(input, { target:{ value:"MK" } });
    fireEvent.click(screen.getByRole("button", { name:"搜索" }));
    await waitFor(() => expect(api.get).toHaveBeenCalledWith(expect.stringContaining("search=MK")));
    expect(screen.getByText("词条：MK")).toBeInTheDocument();
    expect(screen.getByText("解释：密考，家长圈对非公开测试的称呼。")).toBeInTheDocument();

    fireEvent.change(input, { target:{ value:"XSC" } });
    fireEvent.keyDown(input, { key:"Enter" });
    await waitFor(() => expect(api.get).toHaveBeenCalledWith(expect.stringContaining("search=XSC")));
    expect(screen.getByText("词条：XSC")).toBeInTheDocument();

    fireEvent.change(input, { target:{ value:"HD" } });
    fireEvent.click(screen.getByRole("button", { name:"搜索" }));
    await waitFor(() => expect(api.get).toHaveBeenCalledWith(expect.stringContaining("search=HD")));
    expect(screen.getByText("词条：HD")).toBeInTheDocument();
  });

  it("filters and clears an applied search", async () => {
    render(<KnowledgePage />);
    await screen.findByRole("link", { name:"广州小升初XSC完整黑话词典" });
    fireEvent.change(screen.getByLabelText("搜索知识"), { target:{ value:"MK" } });
    fireEvent.click(screen.getByRole("button", { name:"搜索" }));
    await screen.findByRole("button", { name:"清空" });
    fireEvent.click(screen.getByRole("button", { name:"清空" }));
    await waitFor(() => expect(api.get).toHaveBeenCalledWith(expect.not.stringContaining("search=MK")));
    fireEvent.change(screen.getByLabelText("分类筛选"), { target:{ value:"课程资料" } });
    fireEvent.change(screen.getByLabelText("标签筛选"), { target:{ value:"数学" } });
    await waitFor(() => expect(api.get).toHaveBeenCalledWith(expect.stringContaining("tag=%E6%95%B0%E5%AD%A6")));
  });

  it("creates, edits and deletes knowledge", async () => {
    vi.spyOn(window,"confirm").mockReturnValue(true);
    render(<KnowledgePage />);
    await screen.findByRole("link", { name:"广州小升初XSC完整黑话词典" });
    fireEvent.click(screen.getByRole("button", { name:"新增知识" }));
    fireEvent.change(screen.getByLabelText("标题 *"), { target:{ value:"新知识" } });
    fireEvent.change(screen.getByLabelText("分类 *"), { target:{ value:"课程资料" } });
    fireEvent.change(screen.getByLabelText("正文"), { target:{ value:"新的正文" } });
    fireEvent.click(screen.getByRole("button", { name:"保存" }));
    await waitFor(() => expect(api.post).toHaveBeenCalled());
    fireEvent.click(screen.getByRole("button", { name:"编辑" }));
    fireEvent.click(screen.getByRole("button", { name:"保存" }));
    await waitFor(() => expect(api.put).toHaveBeenCalledWith("/knowledge/k1",expect.any(Object)));
    fireEvent.click(screen.getByRole("button", { name:"删除" }));
    await waitFor(() => expect(api.delete).toHaveBeenCalledWith("/knowledge/k1"));
  });
});
