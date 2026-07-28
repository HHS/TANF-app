import { afterEach, describe, expect, it } from "vitest";

const originalEnv = { ...process.env };

afterEach(() => {
  process.env = { ...originalEnv };
});

describe("login redirect routes", () => {
  it("redirects Login.gov requests through the auth host", async () => {
    process.env.NEXT_PUBLIC_AUTH_URL = "https://auth.example.gov";

    const { GET } = await import("./dotgov/route");
    const response = GET();

    expect(response.status).toBe(307);
    expect(response.headers.get("location")).toBe("https://auth.example.gov/login/dotgov");
  });

  it("redirects ACF AMS requests through the auth host", async () => {
    process.env.NEXT_PUBLIC_BACKEND_URL = "https://backend.example.gov/v1";
    delete process.env.NEXT_PUBLIC_AUTH_URL;

    const { GET } = await import("./ams/route");
    const response = GET();

    expect(response.status).toBe(307);
    expect(response.headers.get("location")).toBe("https://backend.example.gov/login/ams");
  });
});