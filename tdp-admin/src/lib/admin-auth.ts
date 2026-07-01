export type BackendHealth = {
  ok: boolean;
  backendUrl: string | null;
  authCheckUrl: string | null;
  status?: number;
  statusText?: string;
  error?: string;
};

export function getBackendBaseUrl() {
  return (
    process.env.NEXT_PUBLIC_BACKEND_URL ||
    process.env.NEXT_PUBLIC_AUTH_URL ||
    null
  );
}

export function getAuthBaseUrl() {
  const authUrl = process.env.NEXT_PUBLIC_AUTH_URL;

  if (authUrl) {
    return authUrl.replace(/\/$/, "");
  }

  const backendUrl = getBackendBaseUrl();

  if (!backendUrl) {
    return null;
  }

  return backendUrl.replace(/\/v1\/?$/, "").replace(/\/$/, "");
}

export function getLoginUrl(provider: "dotgov" | "ams") {
  const authBaseUrl = getAuthBaseUrl();

  if (!authBaseUrl) {
    return null;
  }

  return `${authBaseUrl}/login/${provider}`;
}

export function getProviderLoginPath(provider: "dotgov" | "ams") {
  return `/login/${provider}`;
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