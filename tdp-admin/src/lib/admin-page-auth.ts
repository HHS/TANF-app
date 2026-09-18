import { headers } from "next/headers";
import { forbidden, redirect } from "next/navigation";

import { checkAdminSession, type AdminSession } from "./admin-auth";

export type AuthorizedAdminSession = AdminSession & {
  authenticated: true;
  authorized: true;
};

export type RequiredAdminSessionContext = {
  cookieHeader: string | null;
  requestHeaders: Awaited<ReturnType<typeof headers>>;
  session: AuthorizedAdminSession;
};

export async function requireAdminSession(): Promise<RequiredAdminSessionContext> {
  const requestHeaders = await headers();
  const cookieHeader = requestHeaders.get("cookie");
  const session = await checkAdminSession(cookieHeader);

  if (!session.authenticated) {
    redirect("/login");
  }

  if (session.authorized !== true) {
    forbidden();
  }

  return {
    cookieHeader,
    requestHeaders,
    session: session as AuthorizedAdminSession,
  };
}
