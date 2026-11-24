import NextLink from "next/link";
import AdminShell from "@/components/admin-shell";
import AdminPagination from "@/components/admin-pagination";
import AdminDataLoadError from "@/components/admin-data-load-error";
import { adminApi } from "@/lib/admin-api";
import { readAdminResource } from "@/lib/admin-read";
import {
  parseUserQuery,
  userQueryString,
  userDisplayName,
  USER_STATUSES,
  type SearchParams,
  type UserList,
} from "@/lib/admin-users";
import { requireAdminSession } from "@/lib/require-admin-session";

export const dynamic = "force-dynamic";

export default async function UsersPage({
  searchParams,
}: {
  searchParams: Promise<SearchParams>;
}) {
  const { cookieHeader, requestHeaders, session } = await requireAdminSession();
  const query = parseUserQuery(await searchParams);
  const search = userQueryString(query);
  const result = await readAdminResource<UserList>(() =>
    adminApi.users.list({
      cookieHeader,
      incomingHeaders: requestHeaders,
      sourceRoute: "/users",
      search,
    }),
  );

  return (
    <AdminShell session={session}>
      <div className="admin-users">
        <nav className="admin-users__breadcrumb" aria-label="Breadcrumb">
          <NextLink href="/dashboard">Home</NextLink>
          <span aria-hidden="true">/</span>
          <span aria-current="page">User accounts</span>
        </nav>
        <header className="admin-page-header admin-users__header">
          <h1>User accounts</h1>
          <p>Find a user to review their account, access, and assigned STT.</p>
        </header>
        <section className="admin-user-directory" aria-label="User directory">
          <form
            key={search}
            action="/users"
            method="get"
            className="admin-list-filters"
            aria-label="Search and filter users"
          >
            <div className="admin-list-filters__fields">
              <div className="admin-list-filters__search">
                <label className="usa-label" htmlFor="search">
                  Search by name or email
                </label>
                <input
                  className="usa-input"
                  type="search"
                  id="search"
                  name="search"
                  placeholder="Name or email address"
                  maxLength={150}
                  defaultValue={query.search}
                />
              </div>
              <div>
                <label className="usa-label" htmlFor="status">
                  Approval status
                </label>
                <select
                  className="usa-select"
                  id="status"
                  name="status"
                  defaultValue={query.status}
                >
                  <option value="">All statuses</option>
                  {USER_STATUSES.map((status) => (
                    <option key={status}>{status}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="usa-label" htmlFor="active">
                  Account status
                </label>
                <select
                  className="usa-select"
                  id="active"
                  name="active"
                  defaultValue={query.active}
                >
                  <option value="">All accounts</option>
                  <option value="true">Active</option>
                  <option value="false">Inactive</option>
                </select>
              </div>
            </div>
            <div className="admin-list-filters__toolbar">
              <div className="admin-list-filters__actions">
                <button className="usa-button" type="submit">
                  Apply filters
                </button>
                <NextLink href="/users" className="admin-users__text-link">
                  Clear filters
                </NextLink>
              </div>
              <div className="admin-list-filters__page-size">
                <label className="usa-label" htmlFor="page-size">
                  Users per page
                </label>
                <select
                  className="usa-select"
                  id="page-size"
                  name="page_size"
                  defaultValue={query.pageSize}
                >
                  {[25, 50, 100].map((size) => (
                    <option key={size} value={size}>
                      {size}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </form>
          {!result.ok ? (
            <div className="admin-users__message">
              <AdminDataLoadError
                title={
                  result.status === 404
                    ? "Page not found"
                    : "Could not load users"
                }
                message={
                  result.status === 404
                    ? "This page no longer exists. Return to the first page with your filters."
                    : "User accounts are temporarily unavailable. Please try again."
                }
                href={`/users${userQueryString(query, result.status === 404 ? 1 : query.page)}`}
                action={result.status === 404 ? "First page" : "Try again"}
              />
            </div>
          ) : result.data.count === 0 ? (
            <div className="admin-users__empty" role="status">
              <h2>No users found</h2>
              <p>
                No accounts match your search and filters. Try another name or
                clear your filters.
              </p>
              <NextLink
                className="usa-button usa-button--outline"
                href="/users"
              >
                Clear filters
              </NextLink>
            </div>
          ) : (
            <>
              <div className="admin-users__results-heading">
                <p>
                  {result.data.count === 1
                    ? "1 user"
                    : `${(query.page - 1) * query.pageSize + 1}–${Math.min(query.page * query.pageSize, result.data.count)} of ${result.data.count} users`}
                </p>
                <span>Ordered by last name</span>
              </div>
              <div
                className="admin-table-wrap"
                tabIndex={0}
                role="region"
                aria-label="User accounts table"
              >
                <table className="usa-table usa-table--borderless admin-table admin-users__table">
                  <caption className="usa-sr-only">
                    User accounts, ordered by last name and first name
                  </caption>
                  <thead>
                    <tr>
                      <th scope="col">User</th>
                      <th scope="col">Approval status</th>
                      <th scope="col">STT</th>
                      <th scope="col">Account status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {result.data.results.map((user) => (
                      <tr key={user.id}>
                        <th scope="row">
                          <NextLink
                            className="admin-users__name"
                            href={`/users/${user.id}${search}`}
                            prefetch={false}
                          >
                            {userDisplayName(user)}
                          </NextLink>
                          <span className="admin-table__secondary">
                            {user.email || user.username}
                          </span>
                        </th>
                        <td>
                          <span
                            className="admin-user-status"
                            data-status={user.account_approval_status}
                          >
                            {user.account_approval_status}
                          </span>
                        </td>
                        <td>
                          <span
                            className={
                              user.stt_name ? undefined : "admin-users__muted"
                            }
                          >
                            {user.stt_name || "Not assigned"}
                          </span>
                        </td>
                        <td>
                          <span
                            className="admin-account-status"
                            data-active={user.is_active}
                          >
                            {user.is_active ? "Active" : "Inactive"}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <AdminPagination
                count={result.data.count}
                page={query.page}
                pageSize={query.pageSize}
                href={(page) => `/users${userQueryString(query, page)}`}
              />
            </>
          )}
        </section>
      </div>
    </AdminShell>
  );
}
