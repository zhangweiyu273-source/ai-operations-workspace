export type MetricWrite = {
  account_id: string; metric_date: string; content_title: string; content_url: string | null;
  content_type: string | null; publish_time: string | null; exposure: number; views: number;
  likes: number; comments: number; favorites: number; shares: number; private_messages: number;
  new_leads: number; valid_leads: number; high_intent_leads: number; trial_bookings: number;
  deals: number; revenue: string; notes: string | null;
};
export type Metric = MetricWrite & { id: string; organization_id: string; platform: string; account_name: string; created_by: string | null; updated_by: string | null; created_at: string; updated_at: string };
export type MetricList = { items: Metric[]; total: number; page: number; page_size: number; total_pages: number };
export type Statistics = { exposure: number; views: number; interactions: number; new_leads: number; valid_leads: number; high_intent_leads: number; trial_bookings: number; deals: number; revenue: string; interaction_rate: string; valid_lead_rate: string; trial_conversion_rate: string; deal_rate: string };
export type MetricFilters = { page: number; pageSize: number; dateFrom: string; dateTo: string; platform: string; accountId: string; contentType: string; search: string };
export type ImportResult = { total_rows: number; success_count: number; failed_count: number; duplicate_count: number; errors: { row: number; field: string; message: string }[]; preview: { row: number; metric_date: string; account_name: string; content_title: string; platform: string }[]; can_import: boolean };
export const emptyMetric: MetricWrite = { account_id: "", metric_date: new Date().toISOString().slice(0, 10), content_title: "", content_url: null, content_type: "图文", publish_time: null, exposure: 0, views: 0, likes: 0, comments: 0, favorites: 0, shares: 0, private_messages: 0, new_leads: 0, valid_leads: 0, high_intent_leads: 0, trial_bookings: 0, deals: 0, revenue: "0.00", notes: null };
