import { headers } from "next/headers";
import { forbidden, redirect } from "next/navigation";
import { checkAdminSession } from "@/lib/admin-auth";

export async function requireAdminSession() {
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
    session,
  };
}
