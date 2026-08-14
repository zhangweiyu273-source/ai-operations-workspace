import { apiDownload, apiRequest, apiClient } from "@/lib/api/client";
import type { AccountList } from "@/features/accounts/types";
import type { ImportResult, Metric, MetricFilters, MetricList, MetricWrite, Statistics } from "./types";

export function query(filters: Omit<MetricFilters, "page" | "pageSize">, paging = true, page = 1, pageSize = 20) {
  const value = new URLSearchParams();
  if (paging) { value.set("page", String(page)); value.set("page_size", String(pageSize)); }
  if (filters.dateFrom) value.set("date_from", filters.dateFrom); if (filters.dateTo) value.set("date_to", filters.dateTo);
  if (filters.platform) value.set("platform", filters.platform); if (filters.accountId) value.set("account_id", filters.accountId);
  if (filters.contentType) value.set("content_type", filters.contentType); if (filters.search) value.set("search", filters.search);
  return value.toString();
}
export const listMetrics = (f: MetricFilters) => apiClient.get<MetricList>(`/operation-metrics?${query(f, true, f.page, f.pageSize)}`);
export const statistics = (f: MetricFilters) => apiClient.get<Statistics>(`/operation-metrics/statistics?${query(f, false)}`);
export const createMetric = (v: MetricWrite) => apiClient.post<Metric>("/operation-metrics", v);
export const updateMetric = (id: string, v: MetricWrite) => apiClient.put<Metric>(`/operation-metrics/${id}`, v);
export const deleteMetric = (id: string) => apiClient.delete<void>(`/operation-metrics/${id}`);
export const accountOptions = () => apiClient.get<AccountList>("/accounts?page=1&page_size=100");
export function importMetrics(file: File, confirm = false) { const body = new FormData(); body.append("file", file); return apiRequest<ImportResult>(`/operation-metrics/import?confirm=${confirm}`, { method: "POST", body }); }
export const exportMetrics = (f: MetricFilters) => apiDownload(`/operation-metrics/export?${query(f, false)}`);
