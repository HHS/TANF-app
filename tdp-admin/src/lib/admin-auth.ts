export type BackendHealth = {
  ok: boolean;
  backendUrl: string | null;
  authCheckUrl: string | null;
  status?: number;
  statusText?: string;
  error?: string;
};

export type AdminRole =
  | string
  | {
      id?: number | string;
      name?: string;
      permissions?: unknown[];
      [key: string]: unknown;
    };

export type AdminSession = {
  authenticated: boolean;
  authorized?: boolean;
  csrf?: string;
  user?: {
    email?: string;
    first_name?: string;
    last_name?: string;
    roles?: AdminRole[];
  };
  detail?: string;
};

export function getBackendBaseUrl() {
  return (
    process.env.NEXT_PUBLIC_BACKEND_URL ||
    process.env.NEXT_PUBLIC_AUTH_URL ||
    null
  );
}

function normalizeUrl(url: string) {
  return url.replace(/\/$/, "");
}

function deriveAdminBackendBaseUrl(backendUrl: string) {
  const normalizedBackendUrl = normalizeUrl(backendUrl);

  if (normalizedBackendUrl.endsWith("/admin-api/v1")) {
    return normalizedBackendUrl;
  }

  if (normalizedBackendUrl.endsWith("/v1")) {
    return `${normalizedBackendUrl.slice(0, -"/v1".length)}/admin-api/v1`;
  }

  return `${normalizedBackendUrl}/admin-api/v1`;
}

export function getAdminBackendBaseUrl() {
  const explicitAdminBackendUrl = process.env.ADMIN_BACKEND_URL;

  if (explicitAdminBackendUrl) {
    return normalizeUrl(explicitAdminBackendUrl);
  }

  const backendUrl = getBackendBaseUrl();
  return backendUrl ? deriveAdminBackendBaseUrl(backendUrl) : null;
}

export function getAuthBaseUrl() {
  const authUrl = process.env.NEXT_PUBLIC_AUTH_URL;

  if (authUrl) {
    return normalizeUrl(authUrl);
  }

  const backendUrl = getBackendBaseUrl() ?? getAdminBackendBaseUrl();

  if (!backendUrl) {
    return null;
  }

  return backendUrl
    .replace(/\/admin-api\/v1\/?$/, "")
    .replace(/\/v1\/?$/, "")
    .replace(/\/$/, "");
}

export function getBrowserAuthBaseUrl() {
  const browserAuthUrl = process.env.NEXT_PUBLIC_AUTH_BROWSER_URL;
  return browserAuthUrl ? normalizeUrl(browserAuthUrl) : getAuthBaseUrl();
}

export function getAdminAuthBaseUrl() {
  const authBaseUrl = getAuthBaseUrl();

  if (!authBaseUrl) {
    return null;
  }

  return `${authBaseUrl}/admin-auth`;
}

export function getBrowserAdminAuthBaseUrl() {
  const authBaseUrl = getBrowserAuthBaseUrl();

  if (!authBaseUrl) {
    return null;
  }

  return `${authBaseUrl}/admin-auth`;
}

export function getLoginUrl(provider: "dotgov" | "ams") {
  const authBaseUrl = getAuthBaseUrl();

  if (!authBaseUrl) {
    return null;
  }

  return `${authBaseUrl}/login/${provider}`;
}

export function getAdminLoginUrl(provider: "dotgov" | "ams", nextUrl?: string) {
  const adminAuthBaseUrl = getBrowserAdminAuthBaseUrl();

  if (!adminAuthBaseUrl) {
    return null;
  }

  const loginUrl = new URL(`${adminAuthBaseUrl}/login/${provider}`);
  if (nextUrl) {
    loginUrl.searchParams.set("next", nextUrl);
  }
  return loginUrl.toString();
}

export function getDefaultAdminLoginNextUrl(requestUrl: string) {
  return new URL("/dashboard", new URL(requestUrl).origin).toString();
}

export function getAdminLoginNextUrl(requestUrl: string, nextUrl?: string | null) {
  const fallbackNextUrl = getDefaultAdminLoginNextUrl(requestUrl);

  if (!nextUrl) {
    return fallbackNextUrl;
  }

  const requestOrigin = new URL(requestUrl).origin;

  try {
    const resolvedNextUrl = new URL(nextUrl, requestOrigin);
    return resolvedNextUrl.origin === requestOrigin
      ? resolvedNextUrl.toString()
      : fallbackNextUrl;
  } catch {
    return fallbackNextUrl;
  }
}

export function getAdminAuthCheckUrl() {
  const adminAuthBaseUrl = getAdminAuthBaseUrl();
  return adminAuthBaseUrl ? `${adminAuthBaseUrl}/auth_check` : null;
}

export function getAdminLogoutUrl() {
  const adminAuthBaseUrl = getBrowserAdminAuthBaseUrl();
  return adminAuthBaseUrl ? `${adminAuthBaseUrl}/logout/oidc` : null;
}

export function getProviderLoginPath(provider: "dotgov" | "ams") {
  return `/login/${provider}`;
}

export function getAdminProviderLoginPath(provider: "dotgov" | "ams") {
  return `/login/${provider}`;
}

export function getCsrfTokenFromCookie(cookieHeader: string | null) {
  const match = cookieHeader?.match(/(?:^|;\s*)csrftoken=([^;]*)/);
  return match ? decodeURIComponent(match[1]) : null;
}

export function getAdminCookieHeader(cookieHeader: string | null) {
  if (!cookieHeader) {
    return null;
  }

  const adminSessionCookieName =
    process.env.ADMIN_SESSION_COOKIE_NAME || "admin_sessionid";
  const forwardedCookieNames = new Set([
    adminSessionCookieName,
    "csrftoken",
  ]);
  const adminCookies = cookieHeader
    .split(";")
    .map((cookie) => cookie.trim())
    .filter((cookie) => {
      const separatorIndex = cookie.indexOf("=");
      const name =
        separatorIndex === -1 ? cookie : cookie.slice(0, separatorIndex);
      return forwardedCookieNames.has(name);
    });

  return adminCookies.length ? adminCookies.join("; ") : null;
}

export function buildAdminRequestHeaders({
  cookieHeader,
  csrfToken,
  includeCsrf = false,
  headers = {},
}: {
  cookieHeader?: string | null;
  csrfToken?: string | null;
  includeCsrf?: boolean;
  headers?: HeadersInit;
}) {
  const requestHeaders = new Headers(headers);
  const adminCookieHeader = getAdminCookieHeader(cookieHeader ?? null);

  if (adminCookieHeader) {
    requestHeaders.set("Cookie", adminCookieHeader);
  }

  if (includeCsrf) {
    if (csrfToken) {
      requestHeaders.set("X-CSRFToken", csrfToken);
    }
  }

  return requestHeaders;
}

export async function checkAdminSession(cookieHeader?: string | null): Promise<AdminSession> {
  const adminAuthCheckUrl = getAdminAuthCheckUrl();

  if (!adminAuthCheckUrl) {
    return { authenticated: false, detail: "Admin auth URL is not configured." };
  }

  try {
    const response = await fetch(adminAuthCheckUrl, {
      method: "GET",
      credentials: "include",
      cache: "no-store",
      headers: buildAdminRequestHeaders({ cookieHeader }),
    });
    const data = (await response.json().catch(() => ({}))) as AdminSession;

    if (!response.ok) {
      return {
        ...data,
        authenticated: Boolean(data.authenticated),
        authorized: Boolean(data.authorized),
        detail: data.detail ?? `Admin auth check returned ${response.status}`,
      };
    }

    return data;
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    return { authenticated: false, detail: message };
  }
}

export async function checkBackendHealth(): Promise<BackendHealth> {
  const backendUrl = getBackendBaseUrl();

  if (!backendUrl) {
    return {
      ok: false,
      backendUrl: null,
      authCheckUrl: null,
      error: "NEXT_PUBLIC_BACKEND_URL is not set. Check your environment variables.",
    };
  }

  const normalizedBackendUrl = backendUrl.replace(/\/$/, "");
  const authCheckUrl = `${normalizedBackendUrl}/auth_check`;

  try {
    const response = await fetch(authCheckUrl, {
      method: "GET",
      credentials: "include",
      cache: "no-store",
      signal: AbortSignal.timeout(5000),
    });

    return {
      ok: response.ok,
      backendUrl: normalizedBackendUrl,
      authCheckUrl,
      status: response.status,
      statusText: response.statusText,
      error: response.ok
        ? undefined
        : `Backend auth check returned ${response.status} ${response.statusText}`,
    };
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);

    return {
      ok: false,
      backendUrl: normalizedBackendUrl,
      authCheckUrl,
      error: message,
    };
  }
}
