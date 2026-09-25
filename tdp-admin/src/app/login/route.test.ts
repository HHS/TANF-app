import { afterEach, beforeEach, describe, expect, it } from "vitest";

const originalEnv = { ...process.env };

beforeEach(() => {
  delete process.env.NEXT_PUBLIC_AUTH_BROWSER_URL;
});

afterEach(() => {
  process.env = { ...originalEnv };
});

describe("auth redirect routes", () => {
  it("redirects Login.gov requests through the auth host", async () => {
    process.env.NEXT_PUBLIC_AUTH_URL = "https://auth.example.gov";

    const { GET } = await import("./dotgov/route");
    const response = GET(new Request("https://admin.example.gov/login/dotgov"));

    expect(response.status).toBe(307);
    expect(response.headers.get("location")).toBe(
      "https://auth.example.gov/admin-auth/login/dotgov?next=https%3A%2F%2Fadmin.example.gov%2Fdashboard"
    );
  });

  it("redirects ACF AMS requests through the auth host", async () => {
    process.env.NEXT_PUBLIC_BACKEND_URL = "https://backend.example.gov/v1";
    delete process.env.NEXT_PUBLIC_AUTH_URL;

    const { GET } = await import("./ams/route");
    const response = GET(
      new Request("https://admin.example.gov/login/ams?next=https%3A%2F%2Fadmin.example.gov%2F")
    );

    expect(response.status).toBe(307);
    expect(response.headers.get("location")).toBe(
      "https://backend.example.gov/admin-auth/login/ams?next=https%3A%2F%2Fadmin.example.gov%2F"
    );
  });

  it("defaults ACF AMS next requests to the admin dashboard", async () => {
    process.env.NEXT_PUBLIC_BACKEND_URL = "https://backend.example.gov/v1";
    delete process.env.NEXT_PUBLIC_AUTH_URL;

    const { GET } = await import("./ams/route");
    const response = GET(new Request("https://admin.example.gov/login/ams"));

    expect(response.status).toBe(307);
    expect(response.headers.get("location")).toBe(
      "https://backend.example.gov/admin-auth/login/ams?next=https%3A%2F%2Fadmin.example.gov%2Fdashboard"
    );
  });

  it("falls back to the admin dashboard for cross-origin login return URLs", async () => {
    process.env.NEXT_PUBLIC_AUTH_URL = "https://auth.example.gov";

    const { GET } = await import("./ams/route");
    const response = GET(
      new Request(
        "https://admin.example.gov/login/ams?next=https%3A%2F%2Fevil.example%2F"
      )
    );

    expect(response.status).toBe(307);
    expect(response.headers.get("location")).toBe(
      "https://auth.example.gov/admin-auth/login/ams?next=https%3A%2F%2Fadmin.example.gov%2Fdashboard"
    );
  });

  it("redirects logout through the backend admin logout flow", async () => {
    process.env.NEXT_PUBLIC_AUTH_URL = "https://auth.example.gov";

    const { GET } = await import("../logout/route");
    const response = GET();

    expect(response.status).toBe(307);
    expect(response.headers.get("location")).toBe(
      "https://auth.example.gov/admin-auth/logout/oidc"
    );
    expect(response.headers.get("set-cookie")).toBeNull();
  });
});
