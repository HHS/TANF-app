import { describe, expect, it } from "vitest";
import { parseUserQuery, userQueryString } from "./admin-users";

describe("user list URL state", () => {
  it("normalizes missing, repeated and unsafe query values", () => {
    expect(
      parseUserQuery({
        search: ["a", "b"],
        page: "-5",
        page_size: "100000",
        status: "invalid",
        active: "yes",
      }),
    ).toEqual({ search: "", page: 1, pageSize: 25, status: "", active: "" });
    expect(parseUserQuery({ page: "Infinity" }).page).toBe(1);
    expect(parseUserQuery({ search: "x".repeat(200) }).search).toHaveLength(
      150,
    );
  });

  it("preserves combined filters across pagination, refresh and detail return", () => {
    const query = parseUserQuery({
      search: " a+b@example.com ",
      status: "Access request",
      active: "false",
      page: "3",
      page_size: "50",
    });
    const url = userQueryString(query, 4);
    expect(
      parseUserQuery(Object.fromEntries(new URLSearchParams(url))),
    ).toEqual({ ...query, page: 4 });
    expect(url).toContain("search=a%2Bb%40example.com");
  });
});

import { formatUserDate } from "./admin-users";

it.each([null, "0001-01-01T00:00:00Z", "not-a-date"])(
  "renders unset or invalid timestamp %s safely",
  (value) => {
    expect(formatUserDate(value)).toBe("Not recorded");
  },
);
