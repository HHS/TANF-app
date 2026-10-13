import { describe, expect, it, vi } from "vitest";
vi.mock("next/navigation", () => ({
  redirect: () => {
    throw new Error("LOGIN");
  },
  forbidden: () => {
    throw new Error("FORBIDDEN");
  },
}));
import { readAdminResource } from "./admin-read";

describe("server read states", () => {
  it("keeps empty results successful", async () => {
    await expect(
      readAdminResource(async () => Response.json({ count: 0, results: [] })),
    ).resolves.toEqual({ ok: true, data: { count: 0, results: [] } });
  });
  it.each([404, 500, 503])("preserves HTTP %s as an error", async (status) => {
    await expect(
      readAdminResource(async () => new Response(null, { status })),
    ).resolves.toEqual({ ok: false, status });
  });
  it("handles network and invalid JSON failures", async () => {
    await expect(
      readAdminResource(async () => {
        throw new Error("network");
      }),
    ).resolves.toEqual({ ok: false, status: 503 });
    await expect(
      readAdminResource(async () => new Response("invalid")),
    ).resolves.toEqual({ ok: false, status: 502 });
  });
  it.each([
    [401, "LOGIN"],
    [403, "FORBIDDEN"],
  ] as const)(
    "handles expired or unauthorized sessions (%s)",
    async (status, message) => {
      await expect(
        readAdminResource(async () => new Response(null, { status })),
      ).rejects.toThrow(message);
    },
  );
});
