import NextLink from "next/link";
import type { ReactNode } from "react";
import AdminShell from "@/components/admin-shell";
import AdminDataLoadError from "@/components/admin-data-load-error";
import { adminApi } from "@/lib/admin-api";
import { readAdminResource } from "@/lib/admin-read";
import {
  parseUserQuery,
  userQueryString,
  userDisplayName,
  formatUserDate,
  type SearchParams,
  type AdminUser,
} from "@/lib/admin-users";
import { requireAdminSession } from "@/lib/require-admin-session";

export const dynamic = "force-dynamic";

function UserNotFound({ search }: { search: string }) {
  return (
    <>
      <h1>User details</h1>
      <AdminDataLoadError
        title="User not found"
        message="This account does not exist or is no longer available."
        href={`/users${search}`}
        action="Return to user accounts"
      />
    </>
  );
}

function UserFailedToLoad({ id, search }: { id: string; search: string }) {
  return (
    <>
      <h1>User details</h1>
      <AdminDataLoadError
        title="Could not load user"
        message="Account details are temporarily unavailable. Please try again."
        href={`/users/${encodeURIComponent(id)}${search}`}
        action="Try again"
      />
    </>
  );
}

function UserDetails({ user }: { user: AdminUser }) {
  const details = {
    Username: user.username,
    "Approval status": user.account_approval_status,
    "Account status": user.is_active ? "Active" : "Inactive",
    STT: user.stt_name || "Not assigned",
    Roles: user.roles.join(", ") || "Not assigned",
    "Date joined (Eastern time)": formatUserDate(user.date_joined),
    "Last login (Eastern time)": formatUserDate(user.last_login),
    "Access requested (Eastern time)": formatUserDate(user.access_requested_date),
  };

  return (
    <>
      <header className="admin-page-header">
        <p className="admin-console__eyebrow">User account</p>
        <h1>{userDisplayName(user)}</h1>
        <p>{user.email || user.username}</p>
      </header>
      <section className="admin-dashboard-card" aria-label="Account details">
        <h2>Account details</h2>
        <dl className="admin-success__details">
          {Object.entries(details).map(([label, value]) => (
            <div key={label}>
              <dt>{label}</dt>
              <dd>{value}</dd>
            </div>
          ))}
        </dl>
      </section>
      <p>
        <NextLink href={`/users/${user.id}/edit`}>Edit user account</NextLink>
      </p>
    </>
  );
}

export default async function UserDetailPage({
  params,
  searchParams,
}: {
  params: Promise<{ id: string }>;
  searchParams: Promise<SearchParams>;
}) {
  const { cookieHeader, requestHeaders, session } = await requireAdminSession();
  const { id } = await params;
  const search = userQueryString(parseUserQuery(await searchParams));
  const result = await readAdminResource<AdminUser>(() =>
    adminApi.users.get(id, {
      cookieHeader,
      incomingHeaders: requestHeaders,
      sourceRoute: `/users/${id}`,
    }),
  );

  let content: ReactNode;
  if (result.ok) {
    content = <UserDetails user={result.data} />;
  } else if (result.status === 404) {
    content = <UserNotFound search={search} />;
  } else {
    content = <UserFailedToLoad id={id} search={search} />;
  }

  return (
    <AdminShell session={session}>
      <NextLink href={`/users${search}`}>Back to user accounts</NextLink>
      {content}
    </AdminShell>
  );
}
