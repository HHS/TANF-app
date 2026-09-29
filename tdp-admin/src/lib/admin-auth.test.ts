import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import {
  checkBackendHealth,
  buildAdminRequestHeaders,
  checkAdminSession,
  getAdminBackendBaseUrl,
  getAdminAuthBaseUrl,
  getAdminAuthCheckUrl,
  getAdminCookieHeader,
  getAdminLoginNextUrl,
  getAdminLoginUrl,
  getAdminLogoutUrl,
  getAuthBaseUrl,
  getDefaultAdminLoginNextUrl,
  getBackendBaseUrl,
  getBrowserAuthBaseUrl,
  getCsrfTokenFromCookie,
  getLoginUrl,
  getProviderLoginPath,
} from "./admin-auth";

const originalEnv = { ...process.env };

beforeEach(() => {
  delete process.env.ADMIN_BACKEND_URL;
  delete process.env.NEXT_PUBLIC_AUTH_BROWSER_URL;
});

afterEach(() => {
  process.env = { ...originalEnv };
  vi.restoreAllMocks();
});

describe("admin auth helpers", () => {
  it("prefers the explicit auth URL over the backend URL", () => {
    process.env.NEXT_PUBLIC_AUTH_URL = "https://auth.example.gov/";
    process.env.NEXT_PUBLIC_BACKEND_URL = "https://backend.example.gov/v1";

    expect(getBackendBaseUrl()).toBe("https://backend.example.gov/v1");
    expect(getAdminBackendBaseUrl()).toBe(
      "https://backend.example.gov/admin-api/v1"
    );
    expect(getAuthBaseUrl()).toBe("https://auth.example.gov");
    expect(getLoginUrl("dotgov")).toBe("https://auth.example.gov/login/dotgov");
    expect(getLoginUrl("ams")).toBe("https://auth.example.gov/login/ams");
    expect(getAdminAuthBaseUrl()).toBe("https://auth.example.gov/admin-auth");
    expect(getAdminLoginUrl("ams", "https://admin.example.gov/")).toBe(
      "https://auth.example.gov/admin-auth/login/ams?next=https%3A%2F%2Fadmin.example.gov%2F"
    );
    expect(getAdminAuthCheckUrl()).toBe("https://auth.example.gov/admin-auth/auth_check");
    expect(getAdminLogoutUrl()).toBe("https://auth.example.gov/admin-auth/logout/oidc");
    expect(getProviderLoginPath("dotgov")).toBe("/login/dotgov");
  });

  it("uses a browser-reachable auth URL for redirects when configured", () => {
    process.env.NEXT_PUBLIC_AUTH_URL = "http://host.docker.internal:8989";
    process.env.NEXT_PUBLIC_AUTH_BROWSER_URL = "http://localhost:8989";

    expect(getAuthBaseUrl()).toBe("http://host.docker.internal:8989");
    expect(getBrowserAuthBaseUrl()).toBe("http://localhost:8989");
    expect(getAdminLoginUrl("dotgov")).toBe(
      "http://localhost:8989/admin-auth/login/dotgov"
    );
    expect(getAdminLogoutUrl()).toBe(
      "http://localhost:8989/admin-auth/logout/oidc"
    );
  });

  it("defaults admin login return URLs to the current admin origin dashboard", () => {
    expect(
      getDefaultAdminLoginNextUrl("http://localhost:3002/login/ams")
    ).toBe("http://localhost:3002/dashboard");
    expect(getAdminLoginNextUrl("https://admin.example.gov/login/dotgov")).toBe(
      "https://admin.example.gov/dashboard"
    );
  });

  it("allows only same-origin admin login return URLs", () => {
    expect(
      getAdminLoginNextUrl("http://localhost:3002/login/ams", "/dashboard")
    ).toBe("http://localhost:3002/dashboard");
    expect(
      getAdminLoginNextUrl(
        "http://localhost:3002/login/ams",
        "https://example.gov/bad"
      )
    ).toBe("http://localhost:3002/dashboard");
  });

  it("derives the auth base from the backend URL when needed", () => {
    delete process.env.NEXT_PUBLIC_AUTH_URL;
    process.env.NEXT_PUBLIC_BACKEND_URL = "https://backend.example.gov/v1/";

    expect(getAuthBaseUrl()).toBe("https://backend.example.gov");
    expect(getLoginUrl("dotgov")).toBe("https://backend.example.gov/login/dotgov");
  });

  it("uses an explicit admin backend URL when configured", () => {
    process.env.ADMIN_BACKEND_URL = "https://internal.example.gov/admin-api/v1/";
    process.env.NEXT_PUBLIC_BACKEND_URL = "https://backend.example.gov/v1";

    expect(getAdminBackendBaseUrl()).toBe(
      "https://internal.example.gov/admin-api/v1"
    );
  });

  it("returns a failed backend health result for non-OK responses", async () => {
    process.env.NEXT_PUBLIC_BACKEND_URL = "https://backend.example.gov/v1/";
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => new Response("missing", { status: 404, statusText: "Not Found" }))
    );

    const result = await checkBackendHealth();

    expect(result.ok).toBe(false);
    expect(result.backendUrl).toBe("https://backend.example.gov/v1");
    expect(result.authCheckUrl).toBe("https://backend.example.gov/v1/auth_check");
    expect(result.status).toBe(404);
    expect(result.error).toContain("404");
  });

  it("marks private Cloud Foundry backend requests as HTTPS", async () => {
    process.env.NEXT_PUBLIC_BACKEND_URL =
      "http://tdp-backend-test.apps.internal:8080/v1";
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => Response.json({ authenticated: false }))
    );

    await checkBackendHealth();

    const [, options] = vi.mocked(fetch).mock.calls[0];
    const headers = options?.headers as Headers;
    expect(headers.get("X-Forwarded-Proto")).toBe("https");
  });

  it("forwards explicit Django CSRF context for mutating requests", () => {
    const cookieHeader =
      "sessionid=standard; admin_sessionid=admin; csrftoken=my-csrf-token; preference=compact";
    const headers = buildAdminRequestHeaders({
      cookieHeader,
      csrfToken: "header-csrf-token",
      includeCsrf: true,
    });

    expect(getCsrfTokenFromCookie(cookieHeader)).toBe("my-csrf-token");
    expect(getAdminCookieHeader(cookieHeader)).toBe(
      "admin_sessionid=admin; csrftoken=my-csrf-token"
    );
    expect(headers.get("Cookie")).toBe(
      "admin_sessionid=admin; csrftoken=my-csrf-token"
    );
    expect(headers.get("X-CSRFToken")).toBe("header-csrf-token");
    expect(headers.get("x-service-name")).toBeNull();
  });

  it("does not use cookie CSRF as a header fallback", () => {
    const headers = buildAdminRequestHeaders({
      cookieHeader: "admin_sessionid=abc; csrftoken=my-csrf-token",
      includeCsrf: true,
    });

    expect(headers.get("X-CSRFToken")).toBeNull();
  });

  it("checks the admin-scoped Django session", async () => {
    process.env.NEXT_PUBLIC_AUTH_URL = "https://auth.example.gov";
    vi.stubGlobal(
      "fetch",
      vi.fn(async () =>
        Response.json({
          authenticated: true,
          authorized: true,
          csrf: "csrf-token",
          user: { email: "admin@example.gov" },
        })
      )
    );

    const result = await checkAdminSession("admin_sessionid=abc");

    expect(result.authenticated).toBe(true);
    expect(result.authorized).toBe(true);
    expect(result.csrf).toBe("csrf-token");
    expect(fetch).toHaveBeenCalledWith(
      "https://auth.example.gov/admin-auth/auth_check",
      expect.objectContaining({
        method: "GET",
        credentials: "include",
        cache: "no-store",
      })
    );
  });
});
