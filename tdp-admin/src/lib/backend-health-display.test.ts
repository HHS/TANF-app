import { describe, expect, it } from "vitest";
import { getBackendHealthSummary } from "./backend-health-display";

describe("backend health display", () => {
  it("summarizes a healthy response", () => {
    expect(
      getBackendHealthSummary({
        ok: true,
        backendUrl: "https://backend.example.gov/v1",
        authCheckUrl: "https://backend.example.gov/v1/auth_check",
        status: 200,
        statusText: "OK",
      })
    ).toBe("Reachable (200 OK)");
  });

  it("treats non-OK HTTP responses as a responding backend", () => {
    expect(
      getBackendHealthSummary({
        ok: false,
        backendUrl: "https://backend.example.gov/v1",
        authCheckUrl: "https://backend.example.gov/v1/auth_check",
        status: 401,
        statusText: "Unauthorized",
      })
    ).toBe("Responding (401 Unauthorized)");
  });

  it("summarizes network failures", () => {
    expect(
      getBackendHealthSummary({
        ok: false,
        backendUrl: "https://backend.example.gov/v1",
        authCheckUrl: "https://backend.example.gov/v1/auth_check",
        error: "fetch failed",
      })
    ).toBe("Unavailable (fetch failed)");
  });
});

