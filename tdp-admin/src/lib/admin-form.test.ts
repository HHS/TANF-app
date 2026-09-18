import { describe, expect, it } from "vitest";
import {
  getAdminFormSubmitApiPath,
  getClientValidationRules,
  getDefaultAdminFormValues,
  getFieldErrorMessage,
  type AdminFormMetadata,
} from "./admin-form";

const metadata: AdminFormMetadata = {
  workflow: "users.user.change",
  title: "Edit user",
  object: { id: "user-1", label: "user@example.com" },
  submit_url: "/admin-forms/users.user.change/user-1/",
  fields: [
    {
      name: "username",
      label: "Username",
      type: "text",
      required: true,
      help_text: "",
      initial: "user@example.com",
      choices: [],
      constraints: { max_length: 150 },
    },
    {
      name: "groups",
      label: "Groups",
      type: "multiselect",
      required: false,
      help_text: "",
      initial: ["1"],
      choices: [
        { value: "1", label: "Data Analyst" },
        { value: "2", label: "OFA System Admin" },
      ],
      constraints: {},
    },
    {
      name: "stt",
      label: "STT",
      type: "select",
      required: false,
      help_text: "",
      initial: null,
      choices: [
        { value: "", label: "---------" },
        { value: "42", label: "Test STT" },
      ],
      constraints: {},
    },
  ],
};

describe("admin form metadata helpers", () => {
  it("builds a local proxy submit path without a trailing slash", () => {
    expect(
      getAdminFormSubmitApiPath("/admin-forms/users.user.change/user-1/")
    ).toBe("/api/admin/admin-forms/users.user.change/user-1");
  });

  it("builds React Hook Form defaults from Django metadata", () => {
    expect(getDefaultAdminFormValues(metadata)).toEqual({
      username: "user@example.com",
      groups: ["1"],
      stt: "",
    });
  });

  it("builds generic client validation rules from supported constraints", () => {
    expect(getClientValidationRules(metadata.fields[0])).toMatchObject({
      required: "Username is required.",
      maxLength: {
        value: 150,
        message: "Username must be 150 characters or fewer.",
      },
    });
  });

  it("validates choice values generically", () => {
    const rules = getClientValidationRules(metadata.fields[1]);
    const validate = rules.validate as {
      choice(value: unknown): true | string;
    };

    expect(validate.choice(["1"])).toBe(true);
    expect(validate.choice(["3"])).toBe("Groups includes an unsupported choice.");
  });

  it("joins normalized field errors for display", () => {
    expect(
      getFieldErrorMessage(
        { field_errors: { username: ["Required.", "Must be unique."] } },
        "username"
      )
    ).toBe("Required. Must be unique.");
  });
});
