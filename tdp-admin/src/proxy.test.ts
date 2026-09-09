import { NextRequest } from "next/server";
import { describe, expect, it } from "vitest";
import { proxy } from "./proxy";

describe("admin response cache proxy", () => {
  it("sets no-store headers on admin app responses", () => {
    const response = proxy(
      new NextRequest("https://admin.example.gov/api-validation")
    );

    expect(response.headers.get("Cache-Control")).toBe("no-store");
    expect(response.headers.get("Pragma")).toBe("no-cache");
    expect(response.headers.get("Expires")).toBe("0");
  });
});
