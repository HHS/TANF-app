export const USER_STATUSES = [
  "Initial",
  "Access request",
  "Pending",
  "Approved",
  "Denied",
  "Deactivated",
] as const;

export type SearchParams = Record<string, string | string[] | undefined>;
export type UserQuery = {
  search: string;
  status: string;
  active: string;
  page: number;
  pageSize: number;
};
export type AdminUser = {
  id: string;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  account_approval_status: string;
  stt_name: string | null;
  roles: string[];
  is_active: boolean;
  last_login: string | null;
  date_joined: string;
  access_requested_date: string | null;
};
export type UserList = { count: number; results: AdminUser[] };
export type UserSummary = {
  total: number;
  approved: number;
  access_requests: number;
  pending: number;
};

export function parseUserQuery(params: SearchParams): UserQuery {
  const value = (key: string) =>
    typeof params[key] === "string" ? (params[key] as string) : "";
  const page = Number(value("page"));
  const pageSize = Number(value("page_size"));
  const status = value("status");
  return {
    search: value("search").trim().slice(0, 150),
    status: USER_STATUSES.some((item) => item === status) ? status : "",
    active: ["true", "false"].includes(value("active")) ? value("active") : "",
    page: Number.isSafeInteger(page) && page > 0 ? page : 1,
    pageSize: [25, 50, 100].includes(pageSize) ? pageSize : 25,
  };
}

export function userQueryString(query: UserQuery, page = query.page): string {
  const params = new URLSearchParams();
  for (const key of ["search", "status", "active"] as const) {
    if (query[key]) params.set(key, query[key]);
  }
  params.set("page", String(page));
  params.set("page_size", String(query.pageSize));
  return `?${params.toString()}`;
}

export function userDisplayName(user: AdminUser): string {
  return (
    [user.first_name, user.last_name].filter(Boolean).join(" ") || user.username
  );
}

export function formatUserDate(value: string | null): string {
  // Legacy accounts use year 1 as the unset access-request timestamp.
  if (!value || value.startsWith("0001-")) return "Not recorded";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "Not recorded";
  return new Intl.DateTimeFormat("en-US", {
    dateStyle: "medium",
    timeStyle: "short",
    timeZone: "America/New_York",
  }).format(date);
}
