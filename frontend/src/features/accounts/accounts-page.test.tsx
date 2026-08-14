import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { AccountsPage } from "./accounts-page";
import type { Account, AccountList } from "./types";

const api = vi.hoisted(() => ({
  listAccounts: vi.fn(),
  createAccount: vi.fn(),
  updateAccount: vi.fn(),
  deleteAccount: vi.fn(),
}));

vi.mock("./api", () => api);

const account: Account = {
  id: "00000000-0000-4000-8000-000000000123",
  organization_id: "00000000-0000-4000-8000-000000000001",
  platform: "小红书",
  account_name: "升学规划号",
  account_url: "https://example.test/account",
  account_avatar: null,
  account_type: "品牌账号",
  positioning: "升学规划",
  target_user: "初中家长",
  operator: "运营负责人",
  status: "启用",
  description: "备注",
  created_by: null,
  updated_by: null,
  created_at: "2026-08-14T08:00:00Z",
  updated_at: "2026-08-14T08:00:00Z",
};

const response: AccountList = {
  items: [account],
  total: 1,
  page: 1,
  page_size: 10,
  total_pages: 1,
  summary: { account_count: 1, platform_count: 1, active_count: 1 },
};

describe("AccountsPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    api.listAccounts.mockResolvedValue(response);
    api.createAccount.mockResolvedValue(account);
    api.updateAccount.mockResolvedValue(account);
    api.deleteAccount.mockResolvedValue(undefined);
  });

  it("loads account metrics and table", async () => {
    render(<AccountsPage />);
    expect(await screen.findByRole("button", { name: "升学规划号" })).toBeInTheDocument();
    expect(screen.getByText("初中家长")).toBeInTheDocument();
    expect(api.listAccounts).toHaveBeenCalled();
  });

  it("submits the create form", async () => {
    render(<AccountsPage />);
    await screen.findByRole("button", { name: "升学规划号" });
    fireEvent.click(screen.getByRole("button", { name: "新增账号" }));
    fireEvent.change(screen.getByLabelText(/账号名称/), { target: { value: "数学老师号" } });
    fireEvent.click(screen.getByRole("button", { name: "保存" }));
    await waitFor(() => expect(api.createAccount).toHaveBeenCalledWith(
      expect.objectContaining({ account_name: "数学老师号", platform: "小红书" }),
    ));
  });

  it("edits an account", async () => {
    render(<AccountsPage />);
    await screen.findByRole("button", { name: "升学规划号" });
    fireEvent.click(screen.getByRole("button", { name: "编辑" }));
    fireEvent.change(screen.getByLabelText(/账号名称/), { target: { value: "更新账号" } });
    fireEvent.click(screen.getByRole("button", { name: "保存" }));
    await waitFor(() => expect(api.updateAccount).toHaveBeenCalledWith(
      account.id,
      expect.objectContaining({ account_name: "更新账号" }),
    ));
  });

  it("soft deletes after confirmation", async () => {
    vi.spyOn(window, "confirm").mockReturnValue(true);
    render(<AccountsPage />);
    await screen.findByRole("button", { name: "升学规划号" });
    fireEvent.click(screen.getByRole("button", { name: "删除" }));
    await waitFor(() => expect(api.deleteAccount).toHaveBeenCalledWith(account.id));
  });
});
