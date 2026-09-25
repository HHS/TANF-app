import { describe, expect, it } from "vitest";

import { getAdminLoginErrorMessage } from "./admin-login-errors";

describe("getAdminLoginErrorMessage", () => {
  it("returns validation messages from admin login redirects", () => {
    expect(
      getAdminLoginErrorMessage({
        error: "admin_login_validation",
        message: "Users other than Regional Staff do not get assigned a location",
      })
    ).toBe("Users other than Regional Staff do not get assigned a location");
  });

  it("ignores unknown error codes", () => {
    expect(
      getAdminLoginErrorMessage({
        error: "unknown",
        message: "Do not show this message",
      })
    ).toBe("");
  });

  it("uses a fallback message when the validation redirect has no message", () => {
    expect(
      getAdminLoginErrorMessage({ error: "admin_login_validation" })
    ).toBe("Your account could not be signed in.");
  });

  it("returns generic admin login failure messages", () => {
    expect(
      getAdminLoginErrorMessage({
        error: "admin_login_failed",
        message: "Unable to complete admin sign in.",
      })
    ).toBe("Unable to complete admin sign in.");
  });
});
