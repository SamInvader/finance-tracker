export type Money = number;

export interface User {
  id: number;
  email: string;
  name: string;
  is_demo?: boolean;
}

export interface Preferences {
  currency: string;
  locale: string;
  theme: "light" | "dark" | "system";
  default_time_range: string;
  budget_alert_thresholds: number[];
  dashboard_widgets: string[];
}

export interface Account {
  id: number;
  name: string;
  type: string;
  institution?: string;
  balance: number;
  currency: string;
  notes?: string;
  is_active: boolean;
}

export interface Category {
  id: number;
  name: string;
  kind: "income" | "expense";
  icon: string;
  color: string;
  parent_id?: number | null;
}

export interface Transaction {
  id: number;
  account_id: number;
  destination_account_id?: number | null;
  account_name?: string;
  destination_account_name?: string;
  category_id?: number | null;
  category_name?: string;
  category_color?: string;
  type: "income" | "expense" | "transfer";
  amount: number;
  date: string;
  description?: string;
  notes?: string;
  tags: string[];
  attachments?: { id: number; filename: string; url: string }[];
  attachment_count?: number;
}
