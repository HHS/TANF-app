import { afterEach, describe, expect, it } from "vitest";
import { getHelpUrl, getKnowledgeCenterUrl } from "./help-url";

const originalHelpUrl = process.env.TDP_HELP_URL;

afterEach(() => {
  if (originalHelpUrl === undefined) {
    delete process.env.TDP_HELP_URL;
  } else {
    process.env.TDP_HELP_URL = originalHelpUrl;
  }
});

describe("help URLs", () => {
  it("uses the configured environment URL", () => {
    process.env.TDP_HELP_URL = "https://develop.tanfdata.acf.hhs.gov/help";

    expect(getHelpUrl()).toBe("https://develop.tanfdata.acf.hhs.gov/help/");
    expect(getKnowledgeCenterUrl()).toBe(
      "https://develop.tanfdata.acf.hhs.gov/help/knowledge-center/",
    );
  });

  it("defaults to the local frontend", () => {
    delete process.env.TDP_HELP_URL;

    expect(getHelpUrl()).toBe("http://localhost:3000/help/");
  });
});
