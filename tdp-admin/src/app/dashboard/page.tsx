import NextLink from "next/link";
import AdminShell from "@/components/admin-shell";
import AdminDataLoadError from "@/components/admin-data-load-error";
import { adminApi } from "@/lib/admin-api";
import { readAdminResource } from "@/lib/admin-read";
import type { UserSummary } from "@/lib/admin-users";
import { requireAdminSession } from "@/lib/require-admin-session";

export const dynamic = "force-dynamic";

// TODO: Extract a component per widget as functionality is added so each can own
// its headers, actions, and content without expanding shared config or conditionals.
const widgets = [
  {
    title: "ClamAV File Scans",
    description: "File scan results will appear here.",
    area: "scans",
  },
  {
    title: "OWASP ZAP Scans",
    description: "Frontend and backend security scan results will appear here.",
    area: "security",
  },
  {
    title: "Data Files",
    description: "Recent file processing updates will appear here.",
    area: "files",
  },
  {
    title: "Log Entries",
    description: "Recent activity and nightly task summaries will appear here.",
    area: "logs",
  },
  {
    title: "System Status",
    description:
      "Frontend, backend, Go Parser, and Prometheus status will appear here.",
    area: "system",
  },
  {
    title: "Reparse Meta Model",
    description: "The latest reparse results will appear here.",
    area: "reparse",
  },
  {
    title: "Feedback Submissions",
    description: "Recent feedback submissions will appear here.",
    area: "feedback",
  },
];

const userSummaryItems = [
  {
    label: "Total users",
    count: (summary: UserSummary): number => summary.total,
    href: "/users",
  },
  {
    label: "Approved",
    count: (summary: UserSummary): number => summary.approved,
    href: "/users?status=Approved",
  },
  {
    label: "Access requests",
    count: (summary: UserSummary): number => summary.access_requests,
    href: "/users?status=Access+request",
  },
  {
    label: "Pending",
    count: (summary: UserSummary): number => summary.pending,
    href: "/users?status=Pending",
  },
];

export default async function AdminDashboardPage() {
  const { session, cookieHeader, requestHeaders } = await requireAdminSession();
  const displayName = session.user?.first_name || "admin";
  const summary = await readAdminResource<UserSummary>(() =>
    adminApi.users.summary({
      cookieHeader,
      incomingHeaders: requestHeaders,
      sourceRoute: "/dashboard",
    }),
  );

  return (
    <AdminShell session={session}>
      <header className="admin-page-header admin-dashboard-header">
        <div>
          <h1>Welcome, {displayName}</h1>
          <p>Review user accounts and access requests.</p>
        </div>
        <NextLink className="usa-button usa-button--outline" href="/users">
          Find a user
        </NextLink>
      </header>
      <div className="admin-overview-grid">
        <section
          className="admin-overview-card admin-overview-card--users"
          aria-labelledby="user-summary"
        >
          <h2 id="user-summary">User accounts</h2>
          {summary.ok ? (
            <>
              <p>Current account totals</p>
              <dl className="admin-user-summary">
                {userSummaryItems.map((item) => (
                  <div key={item.label}>
                    <dt>
                      <NextLink href={item.href} className="admin-summary-link">
                        {item.label}
                      </NextLink>
                    </dt>
                    <dd>{item.count(summary.data)}</dd>
                  </div>
                ))}
              </dl>
              <NextLink href="/users">View all user accounts</NextLink>
            </>
          ) : (
            <AdminDataLoadError
              title="Could not load user summary"
              message="Account totals are temporarily unavailable."
              href="/dashboard"
            />
          )}
        </section>
        {widgets.map((widget) => (
          <section
            key={widget.area}
            className={`admin-overview-card admin-overview-card--${widget.area}`}
            aria-labelledby={`widget-${widget.area}`}
          >
            <h2 id={`widget-${widget.area}`}>{widget.title}</h2>
            <span className="admin-status-badge">Not available yet</span>
            <p>{widget.description}</p>
          </section>
        ))}
      </div>
    </AdminShell>
  );
}
