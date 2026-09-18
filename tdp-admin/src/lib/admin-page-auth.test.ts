import { afterEach, describe, expect, it, vi } from "vitest";

const checkAdminSessionMock = vi.hoisted(() => vi.fn());
const forbiddenMock = vi.hoisted(() =>
  vi.fn(() => {
    throw new Error("NEXT_FORBIDDEN");
  })
);
const headersMock = vi.hoisted(() => vi.fn());
const redirectMock = vi.hoisted(() =>
  vi.fn(() => {
    throw new Error("NEXT_REDIRECT");
  })
);

vi.mock("next/headers", () => ({
  headers: headersMock,
}));

vi.mock("next/navigation", () => ({
  forbidden: forbiddenMock,
  redirect: redirectMock,
}));

vi.mock("./admin-auth", () => ({
  checkAdminSession: checkAdminSessionMock,
}));

import { requireAdminSession } from "./admin-page-auth";

afterEach(() => {
  vi.clearAllMocks();
});

describe("admin page auth", () => {
  it("returns request context for authenticated and authorized admin sessions", async () => {
    const requestHeaders = new Headers({ cookie: "admin_sessionid=abc" });
    const session = {
      authenticated: true,
      authorized: true,
      csrf: "csrf-token",
    };
    headersMock.mockResolvedValue(requestHeaders);
    checkAdminSessionMock.mockResolvedValue(session);

    await expect(requireAdminSession()).resolves.toEqual({
      cookieHeader: "admin_sessionid=abc",
      requestHeaders,
      session,
    });
    expect(checkAdminSessionMock).toHaveBeenCalledWith("admin_sessionid=abc");
    expect(redirectMock).not.toHaveBeenCalled();
    expect(forbiddenMock).not.toHaveBeenCalled();
  });

  it("redirects unauthenticated users to login", async () => {
    headersMock.mockResolvedValue(new Headers());
    checkAdminSessionMock.mockResolvedValue({ authenticated: false });

    await expect(requireAdminSession()).rejects.toThrow("NEXT_REDIRECT");

    expect(redirectMock).toHaveBeenCalledWith("/login");
    expect(forbiddenMock).not.toHaveBeenCalled();
  });

  it("forbids authenticated users without admin authorization", async () => {
    headersMock.mockResolvedValue(new Headers());
    checkAdminSessionMock.mockResolvedValue({
      authenticated: true,
      authorized: false,
    });

    await expect(requireAdminSession()).rejects.toThrow("NEXT_FORBIDDEN");

    expect(redirectMock).not.toHaveBeenCalled();
    expect(forbiddenMock).toHaveBeenCalledWith();
  });
});
