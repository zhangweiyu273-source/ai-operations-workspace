import { apiClient } from "@/lib/api/client";
import type { Account, AccountList, AccountWrite } from "./types";

export type AccountFilters = {
  page: number;
  pageSize: number;
  search: string;
  platform: string;
  accountType: string;
  status: string;
};

export function listAccounts(filters: AccountFilters) {
  const query = new URLSearchParams({ page: String(filters.page), page_size: String(filters.pageSize) });
  if (filters.search) query.set("search", filters.search);
  if (filters.platform) query.set("platform", filters.platform);
  if (filters.accountType) query.set("account_type", filters.accountType);
  if (filters.status) query.set("status", filters.status);
  return apiClient.get<AccountList>(`/accounts?${query}`);
}

export const getAccount = (id: string) => apiClient.get<Account>(`/accounts/${id}`);
export const createAccount = (data: AccountWrite) => apiClient.post<Account>("/accounts", data);
export const updateAccount = (id: string, data: AccountWrite) =>
  apiClient.put<Account>(`/accounts/${id}`, data);
export const deleteAccount = (id: string) => apiClient.delete<void>(`/accounts/${id}`);
