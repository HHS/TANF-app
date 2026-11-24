import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { beforeEach, describe, expect, it, vi } from "vitest";
const api = vi.hoisted(() => ({
  list: vi.fn(),
  get: vi.fn(),
  summary: vi.fn(),
}));
vi.mock("@/lib/admin-api", () => ({ adminApi: { users: api } }));
vi.mock("@/lib/require-admin-session", () => ({
  requireAdminSession: async () => ({
    session: { user: { first_name: "Alex" } },
    cookieHeader: "admin_sessionid=test",
    requestHeaders: new Headers(),
  }),
}));
vi.mock("@/components/admin-shell", () => ({
  default: ({ children }: { children: React.ReactNode }) => (
    <main>{children}</main>
  ),
}));
import UsersPage from "./page";
import UserDetailPage from "./[id]/page";
import DashboardPage from "../dashboard/page";
const user = {
  id: "123",
  username: "alex@example.com",
  email: "alex@example.com",
  first_name: "Alex",
  last_name: "Reader",
  account_approval_status: "Pending",
  stt_name: null,
  roles: [],
  is_active: true,
  date_joined: "2026-07-01T12:00:00Z",
  last_login: null,
  access_requested_date: null,
};
beforeEach(() => vi.clearAllMocks());
describe("server-rendered user screens", () => {
  it("requests one bounded page and preserves list context in links", async () => {
    api.list.mockResolvedValue(Response.json({ count: 80, results: [user] }));
    const html = renderToStaticMarkup(
      await UsersPage({
        searchParams: Promise.resolve({
          search: "Alex",
          status: "Pending",
          page: "2",
        }),
      }),
    );
    expect(api.list).toHaveBeenCalledTimes(1);
    expect(api.list.mock.calls[0][0].search).toBe(
      "?search=Alex&status=Pending&page=2&page_size=25",
    );
    expect(html).toContain(
      "/users/123?search=Alex&amp;status=Pending&amp;page=2&amp;page_size=25",
    );
    expect(html).toContain("page=3");
    expect(html).toContain("26–50 of 80 users");
    expect(html).toContain("Not assigned");
  });
  it("distinguishes empty results from backend failure", async () => {
    api.list.mockResolvedValueOnce(Response.json({ count: 0, results: [] }));
    expect(
      renderToStaticMarkup(
        await UsersPage({ searchParams: Promise.resolve({}) }),
      ),
    ).toContain("No users found");
    api.list.mockResolvedValueOnce(new Response(null, { status: 500 }));
    const html = renderToStaticMarkup(
      await UsersPage({ searchParams: Promise.resolve({}) }),
    );
    expect(html).toContain("Could not load users");
    expect(html).not.toContain("No users found");
  });
  it("recovers an out-of-range page with filters intact", async () => {
    api.list.mockResolvedValue(new Response(null, { status: 404 }));
    const html = renderToStaticMarkup(
      await UsersPage({
        searchParams: Promise.resolve({ page: "999", status: "Pending" }),
      }),
    );
    expect(html).toContain("Page not found");
    expect(html).toContain("/users?status=Pending&amp;page=1&amp;page_size=25");
  });
  it("renders a detail and preserves the return URL state", async () => {
    api.get.mockResolvedValue(Response.json(user));
    const html = renderToStaticMarkup(
      await UserDetailPage({
        params: Promise.resolve({ id: user.id }),
        searchParams: Promise.resolve({ search: "Alex", page: "2" }),
      }),
    );
    expect(html).toContain("Alex Reader");
    expect(html).toContain("Not recorded");
    expect(html).toContain("/users?search=Alex&amp;page=2&amp;page_size=25");
    expect(api.get).toHaveBeenCalledTimes(1);
  });
  it("renders a missing user without leaking backend error details", async () => {
    api.get.mockResolvedValue(
      new Response("private debug data", { status: 404 }),
    );
    const html = renderToStaticMarkup(
      await UserDetailPage({
        params: Promise.resolve({ id: "missing" }),
        searchParams: Promise.resolve({ status: "Pending", page: "2" }),
      }),
    );
    expect(html).toContain("User not found");
    expect(html).toContain(
      "This account does not exist or is no longer available.",
    );
    expect(html).toContain(
      '<a href="/users?status=Pending&amp;page=2&amp;page_size=25">Return to user accounts</a>',
    );
    expect(html).not.toContain("Try again");
    expect(html).not.toContain("Edit user account");
    expect(html).not.toContain("private debug data");
  });
  it.each([500, 503])(
    "offers a safe retry URL with list context when user details fail with %i",
    async (status) => {
      api.get.mockResolvedValue(new Response("private debug data", { status }));
      const html = renderToStaticMarkup(
        await UserDetailPage({
          params: Promise.resolve({ id: "user/123" }),
          searchParams: Promise.resolve({ search: "Alex", page: "2" }),
        }),
      );
      expect(html).toContain("Could not load user");
      expect(html).toContain(
        "Account details are temporarily unavailable. Please try again.",
      );
      expect(html).toContain(
        '<a href="/users/user%2F123?search=Alex&amp;page=2&amp;page_size=25">Try again</a>',
      );
      expect(html).not.toContain("User not found");
      expect(html).not.toContain("Edit user account");
      expect(html).not.toContain("private debug data");
    },
  );
  it("keeps unavailable account totals distinct from zero", async () => {
    api.summary.mockResolvedValue(new Response(null, { status: 500 }));
    const html = renderToStaticMarkup(await DashboardPage());
    expect(html).toContain("Could not load user summary");
    expect(html).not.toContain("Current account totals");
    expect(html).toContain("Find a user");
  });
  it("uses aggregate counts on the dashboard and labels unavailable widgets", async () => {
    api.summary.mockResolvedValue(
      Response.json({
        total: 100,
        approved: 70,
        access_requests: 20,
        pending: 10,
      }),
    );
    const html = renderToStaticMarkup(await DashboardPage());
    expect(html).toContain("Welcome, Alex");
    expect(html).toContain("Not available yet");
    expect(html).toContain("/users?status=Access+request");
    expect(html).toContain("100");
    expect(html.indexOf('id="user-summary"')).toBeLessThan(
      html.indexOf('id="widget-scans"'),
    );
    expect(api.list).not.toHaveBeenCalled();
  });
});
