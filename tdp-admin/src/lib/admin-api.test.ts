import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import {
  adminApi,
  getAdminApiUrl,
  isMutatingAdminApiMethod,
  requestAdminApi,
  setAuthenticatedNoStore,
} from "./admin-api";

const originalEnv = { ...process.env };

beforeEach(() => {
  delete process.env.ADMIN_BACKEND_URL;
});

afterEach(() => {
  process.env = { ...originalEnv };
  vi.restoreAllMocks();
});

describe("admin API service", () => {
  it("builds encoded URLs under the Django admin API boundary", () => {
    process.env.NEXT_PUBLIC_BACKEND_URL = "https://backend.example.gov/v1/";

    expect(getAdminApiUrl(["data_files", "file name"], "?page=1")).toBe(
      "https://backend.example.gov/admin-api/v1/data_files/file%20name?page=1"
    );
  });

  it("forwards the scoped session, CSRF token, and server proxy identity", async () => {
    process.env.NEXT_PUBLIC_BACKEND_URL = "https://backend.example.gov/v1";
    process.env.ADMIN_API_PROXY_TOKEN = "server-only-token";
    vi.stubGlobal("fetch", vi.fn(async () => Response.json({ ok: true })));
    const incomingHeaders = new Headers({
      "x-correlation-id": "correlation-123",
      "x-forwarded-for": "203.0.113.9",
      "user-agent": "vitest",
    });

    await requestAdminApi(["users"], {
      method: "PATCH",
      body: JSON.stringify({ active: true }),
      cookieHeader: "admin_sessionid=abc; csrftoken=csrf-cookie",
      csrfToken: "csrf-header",
      incomingHeaders,
      headers: { "content-type": "application/json" },
      sourceRoute: "/api/admin/users",
      requestId: "request-123",
    });

    const [, options] = vi.mocked(fetch).mock.calls[0];
    const headers = options?.headers as Headers;
    expect(options?.method).toBe("PATCH");
    expect(options?.cache).toBe("no-store");
    expect(options?.redirect).toBe("manual");
    expect(headers.get("Cookie")).toBe(
      "admin_sessionid=abc; csrftoken=csrf-cookie"
    );
    expect(headers.get("X-CSRFToken")).toBe("csrf-header");
    expect(headers.get("X-Admin-Proxy-Token")).toBe("server-only-token");
    expect(headers.get("X-Request-ID")).toBe("request-123");
    expect(headers.get("X-TDP-Admin-Source-Route")).toBe("/api/admin/users");
    expect(headers.get("x-correlation-id")).toBe("correlation-123");
    expect(headers.get("x-forwarded-for")).toBe("203.0.113.9");
    expect(headers.get("user-agent")).toBe("vitest");
  });

  it("exposes resource-specific data file reads", async () => {
    process.env.NEXT_PUBLIC_BACKEND_URL = "https://backend.example.gov/v1";
    process.env.ADMIN_API_PROXY_TOKEN = "server-only-token";
    vi.stubGlobal("fetch", vi.fn(async () => Response.json({ id: 42 })));

    await adminApi.dataFiles.get(42, {
      cookieHeader: "admin_sessionid=abc",
    });

    expect(fetch).toHaveBeenCalledWith(
      "https://backend.example.gov/admin-api/v1/data_files/42",
      expect.objectContaining({ method: "GET" })
    );
  });

  it("exposes generic admin form metadata reads", async () => {
    process.env.NEXT_PUBLIC_BACKEND_URL = "https://backend.example.gov/v1";
    process.env.ADMIN_API_PROXY_TOKEN = "server-only-token";
    vi.stubGlobal("fetch", vi.fn(async () => Response.json({ id: "user-1" })));

    await adminApi.adminForms.metadata("users.user.change", "user 1", {
      cookieHeader: "admin_sessionid=abc",
    });

    expect(fetch).toHaveBeenCalledWith(
      "https://backend.example.gov/admin-api/v1/admin-forms/users.user.change/user%201/metadata/",
      expect.objectContaining({ method: "GET" })
    );
  });

  it("identifies mutating methods and disables authenticated caching", () => {
    expect(isMutatingAdminApiMethod("GET")).toBe(false);
    expect(isMutatingAdminApiMethod("patch")).toBe(true);

    const headers = setAuthenticatedNoStore(new Headers());
    expect(headers.get("Cache-Control")).toBe("no-store");
    expect(headers.get("Pragma")).toBe("no-cache");
    expect(headers.get("Expires")).toBe("0");
  });
});
