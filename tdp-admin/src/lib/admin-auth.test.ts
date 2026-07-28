import { afterEach, describe, expect, it, vi } from "vitest";
import {
  checkBackendHealth,
  getAuthBaseUrl,
  getBackendBaseUrl,
  getLoginUrl,
  getProviderLoginPath,
} from "./admin-auth";

const originalEnv = { ...process.env };

afterEach(() => {
  process.env = { ...originalEnv };
  vi.restoreAllMocks();
});

describe("admin auth helpers", () => {
  it("prefers the explicit auth URL over the backend URL", () => {
    process.env.NEXT_PUBLIC_AUTH_URL = "https://auth.example.gov/";
    process.env.NEXT_PUBLIC_BACKEND_URL = "https://backend.example.gov/v1";

    expect(getBackendBaseUrl()).toBe("https://backend.example.gov/v1");
    expect(getAuthBaseUrl()).toBe("https://auth.example.gov");
    expect(getLoginUrl("dotgov")).toBe("https://auth.example.gov/login/dotgov");
    expect(getLoginUrl("ams")).toBe("https://auth.example.gov/login/ams");
    expect(getProviderLoginPath("dotgov")).toBe("/login/dotgov");
  });

  it("derives the auth base from the backend URL when needed", () => {
    delete process.env.NEXT_PUBLIC_AUTH_URL;
    process.env.NEXT_PUBLIC_BACKEND_URL = "https://backend.example.gov/v1/";

    expect(getAuthBaseUrl()).toBe("https://backend.example.gov");
    expect(getLoginUrl("dotgov")).toBe("https://backend.example.gov/login/dotgov");
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
});