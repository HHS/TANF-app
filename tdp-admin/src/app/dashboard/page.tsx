import AdminShell from "@/components/admin-shell";
import { getAdminRoleNames } from "@/lib/admin-navigation";
import { requireAdminSession } from "@/lib/require-admin-session";

export const dynamic = "force-dynamic";

export default async function AdminDashboardPage() {
  const { session } = await requireAdminSession();
  const displayName =
    [session.user?.first_name, session.user?.last_name].filter(Boolean).join(" ") ||
    session.user?.email ||
    "Admin user";
  const roles = getAdminRoleNames(session.user?.roles);

  return (
    <AdminShell session={session}>
      <div className="admin-page-header">
        <p className="admin-console__eyebrow">Dashboard</p>
        <h1>Admin dashboard</h1>
        <p>
          Django validated your admin session and authorized this view.
        </p>
      </div>

      <div className="admin-dashboard-grid">
        <section className="admin-dashboard-card" aria-labelledby="session-summary">
          <h2 id="session-summary">Session summary</h2>
          <dl className="admin-success__details">
            <div>
              <dt>User</dt>
              <dd>{displayName}</dd>
            </div>
            <div>
              <dt>Email</dt>
              <dd>{session.user?.email ?? "Not returned"}</dd>
            </div>
            <div>
              <dt>Roles</dt>
              <dd>{roles.length ? roles.join(", ") : "No roles returned"}</dd>
            </div>
            <div>
              <dt>Session</dt>
              <dd>Authenticated and admin-authorized</dd>
            </div>
          </dl>
        </section>

        <section className="admin-dashboard-card" aria-labelledby="system-actions">
          <h2 id="system-actions">System checks</h2>
          <div className="admin-success__actions">
            <a className="usa-button" href="/api/backend-health">
              Backend health
            </a>
            <a className="usa-button usa-button--outline" href="/api-validation">
              API validation
            </a>
          </div>
        </section>
      </div>
    </AdminShell>
  );
}
