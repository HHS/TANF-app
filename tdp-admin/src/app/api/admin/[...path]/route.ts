import { NextRequest, NextResponse } from "next/server";
import {
  isMutatingAdminApiMethod,
  requestAdminApi,
  setAuthenticatedNoStore,
} from "@/lib/admin-api";

function normalizeOrigin(origin: string) {
  return new URL(origin).origin;
}

function getExpectedAdminOrigin() {
  const expectedOrigin = process.env.ADMIN_FRONTEND_ORIGIN;

  if (!expectedOrigin) {
    return null;
  }

  try {
    return normalizeOrigin(expectedOrigin);
  } catch {
    return null;
  }
}

function validateMutatingRequest(request: NextRequest) {
  const expectedOrigin = getExpectedAdminOrigin();

  if (!expectedOrigin) {
    return {
      response: NextResponse.json(
        {
          ok: false,
          error: "ADMIN_FRONTEND_ORIGIN is not configured.",
        },
        { status: 500 }
      ),
      csrfToken: null,
    };
  }

  const origin = request.headers.get("origin");

  if (!origin) {
    return {
      response: NextResponse.json(
        {
          ok: false,
          error: "Origin header is required for admin API mutations.",
        },
        { status: 403 }
      ),
      csrfToken: null,
    };
  }

  try {
    if (normalizeOrigin(origin) !== expectedOrigin) {
      return {
        response: NextResponse.json(
          {
            ok: false,
            error: "Origin is not allowed for admin API mutations.",
          },
          { status: 403 }
        ),
        csrfToken: null,
      };
    }
  } catch {
    return {
      response: NextResponse.json(
        {
          ok: false,
          error: "Origin header is invalid.",
        },
        { status: 403 }
      ),
      csrfToken: null,
    };
  }

  const csrfToken = request.headers.get("X-CSRFToken")?.trim();

  if (!csrfToken) {
    return {
      response: NextResponse.json(
        {
          ok: false,
          error: "X-CSRFToken header is required for admin API mutations.",
        },
        { status: 403 }
      ),
      csrfToken: null,
    };
  }

  return { response: null, csrfToken };
}

async function proxyAdminRequest(
  request: NextRequest,
  context: { params: Promise<{ path: string[] }> }
) {
  const { path } = await context.params;
  const isMutatingRequest = isMutatingAdminApiMethod(request.method);
  const mutatingRequestValidation = isMutatingRequest
    ? validateMutatingRequest(request)
    : { response: null, csrfToken: null };

  if (mutatingRequestValidation.response) {
    return mutatingRequestValidation.response;
  }

  const cookieHeader = request.headers.get("cookie");
  const headers = new Headers();
  const contentType = request.headers.get("content-type");

  if (contentType) {
    headers.set("content-type", contentType);
  }
  let response: Response;

  try {
    // Django validates the admin session and role on every proxied API request.
    response = await requestAdminApi(path, {
      method: request.method,
      search: request.nextUrl.search,
      body:
        request.method === "GET" || request.method === "HEAD"
          ? undefined
          : await request.text(),
      cookieHeader,
      csrfToken: mutatingRequestValidation.csrfToken,
      incomingHeaders: request.headers,
      headers,
      sourceRoute: request.nextUrl.pathname,
      requestId: request.headers.get("x-request-id"),
    });
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    return NextResponse.json(
      {
        ok: false,
        error: message,
      },
      {
        status: 500,
        headers: setAuthenticatedNoStore(new Headers()),
      }
    );
  }

  const responseHeaders = setAuthenticatedNoStore(new Headers(response.headers));

  return new NextResponse(response.body, {
    status: response.status,
    statusText: response.statusText,
    headers: responseHeaders,
  });
}

export const GET = proxyAdminRequest;
export const POST = proxyAdminRequest;
export const PUT = proxyAdminRequest;
export const PATCH = proxyAdminRequest;
export const DELETE = proxyAdminRequest;
