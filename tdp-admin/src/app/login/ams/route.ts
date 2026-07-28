import { NextResponse } from "next/server";
import { getLoginUrl } from "@/lib/admin-auth";

export function GET() {
  const loginUrl = getLoginUrl("ams");

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