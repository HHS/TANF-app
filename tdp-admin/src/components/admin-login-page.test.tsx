import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it, vi } from "vitest";

const health = vi.hoisted(() => vi.fn());
vi.mock("@/lib/admin-auth", () => ({
  checkBackendHealth: health,
  getAdminLoginUrl: (provider: string) => `/login/${provider}`,
  getAdminProviderLoginPath: (provider: string) => `/login/${provider}`,
}));

import AdminLoginPage from "./admin-login-page";

describe("admin sign-in page", () => {
  it("shows provider choices without infrastructure diagnostics", async () => {
    health.mockResolvedValue({ ok: true, status: 200 });
    const html = renderToStaticMarkup(await AdminLoginPage({}));
    expect(html).toContain('href="/login/dotgov"');
    expect(html).toContain('href="/login/ams"');
    expect(html).not.toContain("Configured backend");
    expect(html).not.toContain("temporarily unavailable");
  });

  it("offers recovery help on a health failure without exposing errors", async () => {
    health.mockResolvedValue({ ok: false, error: "internal-host:8989" });
    const html = renderToStaticMarkup(await AdminLoginPage({}));
    expect(html).toContain("Sign-in services may be temporarily unavailable");
    expect(html).toContain('href="mailto:tanfdata@acf.hhs.gov"');
    expect(html).not.toContain("internal-host");
  });

  it("preserves sign-in error feedback", async () => {
    health.mockResolvedValue({ ok: true });
    const html = renderToStaticMarkup(
      await AdminLoginPage({ loginErrorMessage: "Please try signing in again." }),
    );
    expect(html).toContain('role="alert"');
    expect(html).toContain("Please try signing in again.");
  });
});
