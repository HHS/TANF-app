import { NextResponse } from "next/server";
import { getAdminLoginUrl } from "@/lib/admin-auth";

export function GET(request: Request) {
  const nextUrl = new URL(request.url).searchParams.get("next") ?? undefined;
  const loginUrl = getAdminLoginUrl("ams", nextUrl);

  if (!loginUrl) {
    return NextResponse.json(
      {
        ok: false,
        error: "NEXT_PUBLIC_AUTH_URL or NEXT_PUBLIC_BACKEND_URL is not configured.",
      },
      { status: 500 }
    );
  }

  return NextResponse.redirect(loginUrl, { status: 307 });
}
