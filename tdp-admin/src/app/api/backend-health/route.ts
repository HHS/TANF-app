import { NextResponse } from "next/server";
import { checkBackendHealth } from "@/lib/admin-auth";

/**
 * GET /api/backend-health
 *
 * Server-side route handler that reads NEXT_PUBLIC_BACKEND_URL from the
 * environment and calls Django's /auth_check endpoint. Used to verify that
 * the admin app can reach the Django backend through configured env vars.
 *
 * Returns:
 *   { backendUrl, status, ok, error? }
 */
export async function GET() {
  try {
    const backend = await checkBackendHealth();

    if (!backend.ok) {
      return NextResponse.json(
        {
          ...backend,
          error: backend.error ?? "Backend auth check returned a non-OK response.",
        },
        { status: backend.status ?? 502 }
      );
    }

    return NextResponse.json({
      ...backend,
    });
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    return NextResponse.json(
      {
        ok: false,
        backendUrl: null,
        authCheckUrl: null,
        error: message,
      },
      { status: 502 }
    );
  }
}
