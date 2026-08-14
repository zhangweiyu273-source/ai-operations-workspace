export type AccountStatus = "启用" | "停用" | "测试中";

export type AccountWrite = {
  platform: string;
  account_name: string;
  account_url: string | null;
  account_avatar?: string | null;
  account_type: string;
  positioning: string | null;
  target_user: string | null;
  operator: string | null;
  status: AccountStatus;
  description: string | null;
};

export type Account = AccountWrite & {
  id: string;
  organization_id: string;
  created_by: string | null;
  updated_by: string | null;
  created_at: string;
  updated_at: string;
};

export type AccountList = {
  items: Account[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
  summary: { account_count: number; platform_count: number; active_count: number };
};

export const emptyAccount: AccountWrite = {
  platform: "小红书",
  account_name: "",
  account_url: null,
  account_type: "品牌账号",
  positioning: null,
  target_user: null,
  operator: null,
  status: "启用",
  description: null,
};
