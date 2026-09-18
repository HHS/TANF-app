import { NextRequest } from "next/server";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { GET, PATCH, POST } from "./route";

const originalEnv = { ...process.env };

beforeEach(() => {
  delete process.env.ADMIN_BACKEND_URL;
});

afterEach(() => {
  process.env = { ...originalEnv };
  vi.restoreAllMocks();
});

describe("admin API proxy", () => {
  it("proxies through the admin backend path without a service header", async () => {
    process.env.NEXT_PUBLIC_BACKEND_URL = "https://backend.example.gov/v1";
    process.env.ADMIN_API_PROXY_TOKEN = "server-only-token";
    vi.stubGlobal("fetch", vi.fn(async () => Response.json({ ok: true })));

    const request = new NextRequest(
      "https://admin.example.gov/api/admin/users?active=true",
      {
        headers: {
          cookie:
            "sessionid=standard; admin_sessionid=abc; csrftoken=csrf-token",
          "x-correlation-id": "correlation-123",
          "x-forwarded-for": "203.0.113.9",
        },
      }
    );

    const response = await GET(request, {
      params: Promise.resolve({ path: ["users"] }),
    });

    expect(response.status).toBe(200);
    expect(fetch).toHaveBeenCalledTimes(1);
    expect(fetch).toHaveBeenCalledWith(
      "https://backend.example.gov/admin-api/v1/users?active=true",
      expect.objectContaining({
        method: "GET",
        credentials: "include",
        cache: "no-store",
      })
    );

    const [, options] = vi.mocked(fetch).mock.calls[0];
    const headers = options?.headers as Headers;
    expect(headers.get("Cookie")).toBe(
      "admin_sessionid=abc; csrftoken=csrf-token"
    );
    expect(headers.get("x-service-name")).toBeNull();
    expect(headers.get("X-Admin-Proxy-Token")).toBe("server-only-token");
    expect(headers.get("x-correlation-id")).toBe("correlation-123");
    expect(headers.get("x-forwarded-for")).toBe("203.0.113.9");
  });

  it("returns Django admin authorization failures", async () => {
    process.env.NEXT_PUBLIC_BACKEND_URL = "https://backend.example.gov/v1";
    process.env.ADMIN_API_PROXY_TOKEN = "server-only-token";
    vi.stubGlobal(
      "fetch",
      vi.fn(async () =>
        Response.json(
          {
            authenticated: true,
            authorized: false,
            detail: "User is not authorized for the admin console.",
          },
          { status: 403 }
        )
      )
    );

    const request = new NextRequest(
      "https://admin.example.gov/api/admin/users",
      {
        headers: {
          cookie: "admin_sessionid=abc",
        },
      }
    );

    const response = await GET(request, {
      params: Promise.resolve({ path: ["users"] }),
    });
    const data = await response.json();

    expect(response.status).toBe(403);
    expect(data).toEqual({
      authenticated: true,
      authorized: false,
      detail: "User is not authorized for the admin console.",
    });
    expect(fetch).toHaveBeenCalledTimes(1);
    expect(fetch).toHaveBeenCalledWith(
      "https://backend.example.gov/admin-api/v1/users",
      expect.any(Object)
    );
  });

  it("returns Django admin authentication failures", async () => {
    process.env.NEXT_PUBLIC_BACKEND_URL = "https://backend.example.gov/v1";
    process.env.ADMIN_API_PROXY_TOKEN = "server-only-token";
    vi.stubGlobal(
      "fetch",
      vi.fn(async () =>
        Response.json(
          {
            authenticated: false,
            detail: "Admin authentication is required.",
          },
          { status: 401 }
        )
      )
    );

    const request = new NextRequest("https://admin.example.gov/api/admin/users");

    const response = await GET(request, {
      params: Promise.resolve({ path: ["users"] }),
    });
    const data = await response.json();

    expect(response.status).toBe(401);
    expect(data).toEqual({
      authenticated: false,
      detail: "Admin authentication is required.",
    });
    expect(fetch).toHaveBeenCalledTimes(1);
  });

  it("forwards CSRF context for mutating requests", async () => {
    process.env.NEXT_PUBLIC_BACKEND_URL = "https://backend.example.gov/v1";
    process.env.ADMIN_API_PROXY_TOKEN = "server-only-token";
    process.env.ADMIN_FRONTEND_ORIGIN = "https://admin.example.gov";
    vi.stubGlobal("fetch", vi.fn(async () => Response.json({ ok: true })));

    const request = new NextRequest("https://admin.example.gov/api/admin/users", {
      method: "POST",
      body: JSON.stringify({ active: true }),
      headers: {
        "content-type": "application/json",
        "X-CSRFToken": "header-csrf-token",
        cookie: "admin_sessionid=abc; csrftoken=cookie-csrf-token",
        origin: "https://admin.example.gov",
      },
    });

    const response = await POST(request, {
      params: Promise.resolve({ path: ["users"] }),
    });

    expect(response.status).toBe(200);
    expect(fetch).toHaveBeenCalledTimes(1);
    expect(fetch).toHaveBeenCalledWith(
      "https://backend.example.gov/admin-api/v1/users/",
      expect.any(Object)
    );

    const [, options] = vi.mocked(fetch).mock.calls[0];
    const headers = options?.headers as Headers;
    expect(options?.method).toBe("POST");
    expect(options?.body).toBe(JSON.stringify({ active: true }));
    expect(headers.get("content-type")).toBe("application/json");
    expect(headers.get("X-CSRFToken")).toBe("header-csrf-token");
    expect(headers.get("X-Admin-Proxy-Token")).toBe("server-only-token");
  });

  it("uses a trailing slash for PATCH requests forwarded to Django", async () => {
    process.env.NEXT_PUBLIC_BACKEND_URL = "https://backend.example.gov/v1";
    process.env.ADMIN_API_PROXY_TOKEN = "server-only-token";
    process.env.ADMIN_FRONTEND_ORIGIN = "https://admin.example.gov";
    vi.stubGlobal("fetch", vi.fn(async () => Response.json({ ok: true })));

    const request = new NextRequest(
      "https://admin.example.gov/api/admin/admin-forms/users.user.change/user-1",
      {
        method: "PATCH",
        body: JSON.stringify({ first_name: "Updated" }),
        headers: {
          "content-type": "application/json",
          "X-CSRFToken": "header-csrf-token",
          cookie: "admin_sessionid=abc; csrftoken=cookie-csrf-token",
          origin: "https://admin.example.gov",
        },
      }
    );

    const response = await PATCH(request, {
      params: Promise.resolve({
        path: ["admin-forms", "users.user.change", "user-1"],
      }),
    });

    expect(response.status).toBe(200);
    expect(fetch).toHaveBeenCalledWith(
      "https://backend.example.gov/admin-api/v1/admin-forms/users.user.change/user-1/",
      expect.objectContaining({
        method: "PATCH",
        body: JSON.stringify({ first_name: "Updated" }),
      })
    );
  });

  it("fails closed when the admin frontend origin is not configured for mutations", async () => {
    process.env.NEXT_PUBLIC_BACKEND_URL = "https://backend.example.gov/v1";
    process.env.ADMIN_API_PROXY_TOKEN = "server-only-token";
    delete process.env.ADMIN_FRONTEND_ORIGIN;
    vi.stubGlobal("fetch", vi.fn());

    const request = new NextRequest("https://admin.example.gov/api/admin/users", {
      method: "POST",
      body: JSON.stringify({ active: true }),
      headers: {
        "X-CSRFToken": "csrf-token",
        origin: "https://admin.example.gov",
      },
    });

    const response = await POST(request, {
      params: Promise.resolve({ path: ["users"] }),
    });
    const data = await response.json();

    expect(response.status).toBe(500);
    expect(data.error).toBe("ADMIN_FRONTEND_ORIGIN is not configured.");
    expect(fetch).not.toHaveBeenCalled();
  });

  it("rejects mutating requests from unexpected origins", async () => {
    process.env.NEXT_PUBLIC_BACKEND_URL = "https://backend.example.gov/v1";
    process.env.ADMIN_API_PROXY_TOKEN = "server-only-token";
    process.env.ADMIN_FRONTEND_ORIGIN = "https://admin.example.gov";
    vi.stubGlobal("fetch", vi.fn());

    const request = new NextRequest("https://admin.example.gov/api/admin/users", {
      method: "POST",
      body: JSON.stringify({ active: true }),
      headers: {
        "X-CSRFToken": "csrf-token",
        origin: "https://evil.example.gov",
      },
    });

    const response = await POST(request, {
      params: Promise.resolve({ path: ["users"] }),
    });
    const data = await response.json();

    expect(response.status).toBe(403);
    expect(data.error).toBe("Origin is not allowed for admin API mutations.");
    expect(fetch).not.toHaveBeenCalled();
  });

  it("rejects mutating requests without a CSRF header", async () => {
    process.env.NEXT_PUBLIC_BACKEND_URL = "https://backend.example.gov/v1";
    process.env.ADMIN_API_PROXY_TOKEN = "server-only-token";
    process.env.ADMIN_FRONTEND_ORIGIN = "https://admin.example.gov";
    vi.stubGlobal("fetch", vi.fn());

    const request = new NextRequest("https://admin.example.gov/api/admin/users", {
      method: "POST",
      body: JSON.stringify({ active: true }),
      headers: {
        cookie: "admin_sessionid=abc; csrftoken=cookie-csrf-token",
        origin: "https://admin.example.gov",
      },
    });

    const response = await POST(request, {
      params: Promise.resolve({ path: ["users"] }),
    });
    const data = await response.json();

    expect(response.status).toBe(403);
    expect(data.error).toBe(
      "X-CSRFToken header is required for admin API mutations."
    );
    expect(fetch).not.toHaveBeenCalled();
  });

  it("fails closed when the proxy token is not configured", async () => {
    process.env.NEXT_PUBLIC_BACKEND_URL = "https://backend.example.gov/v1";
    delete process.env.ADMIN_API_PROXY_TOKEN;
    vi.stubGlobal("fetch", vi.fn());

    const request = new NextRequest("https://admin.example.gov/api/admin/users");

    const response = await GET(request, {
      params: Promise.resolve({ path: ["users"] }),
    });
    const data = await response.json();

    expect(response.status).toBe(500);
    expect(data.error).toBe("ADMIN_API_PROXY_TOKEN is not configured.");
    expect(fetch).not.toHaveBeenCalled();
  });
});
