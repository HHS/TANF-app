export type AdminFormChoice = {
  value: string;
  label: string;
};

export type AdminFormConstraints = {
  max_length?: number;
  min_length?: number;
  max_value?: number;
  min_value?: number;
  pattern?: string;
};

export type AdminFormField = {
  name: string;
  label: string;
  type:
    | "text"
    | "email"
    | "number"
    | "textarea"
    | "select"
    | "multiselect"
    | "checkbox";
  required: boolean;
  help_text: string;
  initial: string | string[] | boolean | number | null;
  choices: AdminFormChoice[];
  constraints: AdminFormConstraints;
};

export type AdminFormMetadata = {
  workflow: string;
  title: string;
  object: {
    id: string;
    label: string;
  };
  submit_url: string;
  fields: AdminFormField[];
};

export type AdminFormValues = Record<string, string | string[] | boolean>;

export type NormalizedAdminFormErrors = {
  field_errors?: Record<string, string[]>;
  non_field_errors?: string[];
};

export function getAdminFormSubmitApiPath(submitUrl: string) {
  const submitPath = submitUrl.startsWith("/") ? submitUrl : `/${submitUrl}`;
  const normalizedSubmitPath =
    submitPath.length > 1 && submitPath.endsWith("/")
      ? submitPath.slice(0, -1)
      : submitPath;

  return `/api/admin${normalizedSubmitPath}`;
}

export function getDefaultAdminFormValues(
  metadata: AdminFormMetadata
): AdminFormValues {
  return metadata.fields.reduce<AdminFormValues>((values, field) => {
    if (field.type === "multiselect") {
      values[field.name] = Array.isArray(field.initial)
        ? field.initial.map(String)
        : [];
      return values;
    }

    if (field.type === "checkbox") {
      values[field.name] = Boolean(field.initial);
      return values;
    }

    values[field.name] =
      field.initial === null || Array.isArray(field.initial)
        ? ""
        : String(field.initial);
    return values;
  }, {});
}

export function getFieldErrorMessage(
  errors: NormalizedAdminFormErrors,
  fieldName: string
) {
  return errors.field_errors?.[fieldName]?.join(" ") ?? "";
}

export function getClientValidationRules(field: AdminFormField) {
  const rules: Record<string, unknown> = {};
  const constraints = field.constraints ?? {};

  if (field.required) {
    rules.required = `${field.label} is required.`;
  }

  if (constraints.max_length !== undefined) {
    rules.maxLength = {
      value: constraints.max_length,
      message: `${field.label} must be ${constraints.max_length} characters or fewer.`,
    };
  }

  if (constraints.min_length !== undefined) {
    rules.minLength = {
      value: constraints.min_length,
      message: `${field.label} must be at least ${constraints.min_length} characters.`,
    };
  }

  if (constraints.max_value !== undefined) {
    rules.max = {
      value: constraints.max_value,
      message: `${field.label} must be ${constraints.max_value} or less.`,
    };
  }

  if (constraints.min_value !== undefined) {
    rules.min = {
      value: constraints.min_value,
      message: `${field.label} must be at least ${constraints.min_value}.`,
    };
  }

  if (constraints.pattern) {
    try {
      rules.pattern = {
        value: new RegExp(constraints.pattern),
        message: `${field.label} has an invalid format.`,
      };
    } catch {
      // Invalid server patterns are ignored client-side; Django remains authoritative.
    }
  }

  if (field.choices.length) {
    const allowedChoices = new Set(field.choices.map((choice) => choice.value));
    rules.validate = {
      choice: (value: unknown) => {
        const values = Array.isArray(value) ? value : [value];
        const populatedValues = values
          .map((item) => String(item ?? ""))
          .filter((item) => item !== "");

        if (!populatedValues.length) {
          return field.required ? `${field.label} is required.` : true;
        }

        return populatedValues.every((item) => allowedChoices.has(item))
          ? true
          : `${field.label} includes an unsupported choice.`;
      },
    };
  }

  return rules;
}
