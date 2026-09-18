import { notFound } from "next/navigation";
import { AdminForm } from "@/components/admin-form";
import AdminShell from "@/components/admin-shell";
import { adminApi } from "@/lib/admin-api";
import type { AdminFormMetadata } from "@/lib/admin-form";
import { requireAdminSession } from "@/lib/require-admin-session";

export const dynamic = "force-dynamic";
const USER_ADMIN_WORKFLOW = "users.user.change";

export default async function UserEditPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { cookieHeader, requestHeaders, session } = await requireAdminSession();

  const { id } = await params;
  const response = await adminApi.adminForms.metadata(USER_ADMIN_WORKFLOW, id, {
    cookieHeader,
    incomingHeaders: requestHeaders,
    sourceRoute: `/users/${id}/edit`,
  });

  if (response.status === 404) {
    notFound();
  }

  const metadata = (await response
    .json()
    .catch(() => null)) as AdminFormMetadata | null;

  return (
    <AdminShell session={session}>
      <section className="admin-success" aria-label="Edit user">
        <div className="admin-success__panel admin-success__panel--form">
          <p className="admin-console__eyebrow">Users</p>
          <h1>{metadata?.object.label ?? "Edit user"}</h1>

          {!response.ok || !metadata ? (
            <div
              className="usa-alert usa-alert--error admin-form__alert"
              role="alert"
            >
              <div className="usa-alert__body">
                <h2 className="usa-alert__heading">Could not load user form</h2>
              </div>
            </div>
          ) : (
            <AdminForm
              metadata={metadata}
              csrfToken={session.csrf ?? null}
              cancelHref="/users"
              cancelLabel="Back to users"
            />
          )}
        </div>
      </section>
    </AdminShell>
  );
}
