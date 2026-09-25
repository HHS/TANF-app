"use client";

import { useState } from "react";
import {
  Alert,
  Button,
  ErrorMessage,
  FormGroup,
  Label,
  Select as UswdsSelect,
  Textarea as UswdsTextarea,
  TextInput as UswdsTextInput,
} from "@trussworks/react-uswds";
import {
  useForm,
  type FieldError,
  type RegisterOptions,
  type UseFormRegisterReturn,
} from "react-hook-form";
import {
  getAdminFormSubmitApiPath,
  getClientValidationRules,
  getDefaultAdminFormValues,
  type AdminFormField as AdminFormFieldMetadata,
  type AdminFormMetadata,
  type AdminFormValues,
  type NormalizedAdminFormErrors,
} from "@/lib/admin-form";

type AdminFormProps = {
  metadata: AdminFormMetadata;
  csrfToken: string | null;
  cancelHref?: string;
  cancelLabel?: string;
};

type AdminFormMutationResponse = {
  ok?: boolean;
  errors?: NormalizedAdminFormErrors;
  metadata?: AdminFormMetadata;
};

type FormFieldProps = {
  field: AdminFormFieldMetadata;
  error?: FieldError;
  registration: UseFormRegisterReturn;
};

type FieldInputProps = FieldInputControlProps & {
  type: AdminFormFieldMetadata["type"];
};

type FieldInputControlProps = {
  field: AdminFormFieldMetadata;
  hasError: boolean;
  id: string;
  registration: UseFormRegisterReturn;
  describedById?: string;
};

function fieldId(field: AdminFormFieldMetadata) {
  return `admin-field-${field.name}`;
}

function describedBy(field: AdminFormFieldMetadata, hasError: boolean) {
  const ids = [];

  if (field.help_text) {
    ids.push(`${fieldId(field)}-hint`);
  }

  if (hasError) {
    ids.push(`${fieldId(field)}-error`);
  }

  return ids.length ? ids.join(" ") : undefined;
}

function fieldErrorMessage(error?: FieldError) {
  return typeof error?.message === "string" ? error.message : "";
}

function FieldLabel({
  field,
  hasError,
}: {
  field: AdminFormFieldMetadata;
  hasError: boolean;
}) {
  if (field.type === "checkbox") {
    return null;
  }

  return (
    <Label
      htmlFor={fieldId(field)}
      error={hasError}
      requiredMarker={field.required}
    >
      {field.label}
    </Label>
  );
}

function SelectInput({
  field,
  hasError,
  id,
  registration,
  describedById,
}: FieldInputControlProps) {
  return (
    <UswdsSelect
      id={id}
      name={registration.name}
      inputRef={registration.ref}
      onBlur={registration.onBlur}
      onChange={registration.onChange}
      validationStatus={hasError ? "error" : undefined}
      aria-describedby={describedById}
    >
      {field.choices.map((choice) => (
        <option key={`${field.name}-${choice.value}`} value={choice.value}>
          {choice.label}
        </option>
      ))}
    </UswdsSelect>
  );
}

function MultiSelectInput({
  field,
  hasError,
  id,
  registration,
  describedById,
}: FieldInputControlProps) {
  return (
    <UswdsSelect
      id={id}
      name={registration.name}
      inputRef={registration.ref}
      onBlur={registration.onBlur}
      onChange={registration.onChange}
      validationStatus={hasError ? "error" : undefined}
      aria-describedby={describedById}
      multiple
      size={Math.min(Math.max(field.choices.length, 3), 8)}
    >
      {field.choices
        .filter((choice) => choice.value !== "")
        .map((choice) => (
          <option key={`${field.name}-${choice.value}`} value={choice.value}>
            {choice.label}
          </option>
        ))}
    </UswdsSelect>
  );
}

function CheckboxInput({
  field,
  id,
  registration,
  describedById,
}: FieldInputControlProps) {
  return (
    <div className="usa-checkbox">
      <input
        className="usa-checkbox__input"
        id={id}
        type="checkbox"
        aria-describedby={describedById}
        {...registration}
      />
      <label className="usa-checkbox__label" htmlFor={id}>
        {field.label}
        {field.required && (
          <abbr title="required" className="usa-hint usa-hint--required">
            *
          </abbr>
        )}
      </label>
    </div>
  );
}

function TextareaInput({
  hasError,
  id,
  registration,
  describedById,
}: FieldInputControlProps) {
  return (
    <UswdsTextarea
      id={id}
      name={registration.name}
      inputRef={registration.ref}
      onBlur={registration.onBlur}
      onChange={registration.onChange}
      error={hasError}
      aria-describedby={describedById}
    />
  );
}

function TextInput({
  hasError,
  id,
  registration,
  describedById,
  type,
}: FieldInputControlProps & { type: "email" | "number" | "text" }) {
  return (
    <UswdsTextInput
      id={id}
      type={type}
      validationStatus={hasError ? "error" : undefined}
      aria-describedby={describedById}
      {...registration}
    />
  );
}

function textInputType(type: AdminFormFieldMetadata["type"]) {
  return type === "number" || type === "email" ? type : "text";
}

function FieldInput({ type, ...inputProps }: FieldInputProps) {
  switch (type) {
    case "select":
      return <SelectInput {...inputProps} />;
    case "multiselect":
      return <MultiSelectInput {...inputProps} />;
    case "checkbox":
      return <CheckboxInput {...inputProps} />;
    case "textarea":
      return <TextareaInput {...inputProps} />;
    default:
      return <TextInput type={textInputType(type)} {...inputProps} />;
  }
}

function FormField({ field, error, registration }: FormFieldProps) {
  const message = fieldErrorMessage(error);
  const hasError = Boolean(message);
  const id = fieldId(field);
  const describedById = describedBy(field, hasError);
  const inputProps = {
    field,
    hasError,
    id,
    registration,
    describedById,
  };

  return (
    <FormGroup error={hasError}>
      <FieldLabel field={field} hasError={hasError} />
      {field.help_text && (
        <div className="usa-hint" id={`${id}-hint`}>
          {field.help_text}
        </div>
      )}
      {hasError && <ErrorMessage id={`${id}-error`}>{message}</ErrorMessage>}
      <FieldInput type={field.type} {...inputProps} />
    </FormGroup>
  );
}

export function AdminForm({
  metadata,
  csrfToken,
  cancelHref,
  cancelLabel = "Back",
}: AdminFormProps) {
  const [formMetadata, setFormMetadata] = useState(metadata);
  const [serverErrors, setServerErrors] = useState<string[]>([]);
  const [statusMessage, setStatusMessage] = useState("");
  const {
    register,
    handleSubmit,
    reset,
    setError,
    formState: { errors, isSubmitting },
  } = useForm<AdminFormValues>({
    defaultValues: getDefaultAdminFormValues(metadata),
    mode: "onBlur",
    reValidateMode: "onChange",
  });

  function applyServerErrors(normalizedErrors?: NormalizedAdminFormErrors) {
    setServerErrors(normalizedErrors?.non_field_errors ?? []);

    for (const [name, messages] of Object.entries(
      normalizedErrors?.field_errors ?? {}
    )) {
      setError(name, {
        type: "server",
        message: messages.join(" "),
      });
    }
  }

  async function submit(values: AdminFormValues) {
    setServerErrors([]);
    setStatusMessage("");

    if (!csrfToken) {
      setServerErrors(["A CSRF token is required before saving this form."]);
      return;
    }

    const response = await fetch(
      getAdminFormSubmitApiPath(formMetadata.submit_url),
      {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken,
        },
        body: JSON.stringify(values),
      }
    );
    const data = (await response
      .json()
      .catch(() => ({}))) as AdminFormMutationResponse;

    if (!response.ok || data.ok === false) {
      if (data.errors) {
        applyServerErrors(data.errors);
      } else {
        setServerErrors([`Save failed with status ${response.status}.`]);
      }
      return;
    }

    if (data.metadata) {
      setFormMetadata(data.metadata);
      reset(getDefaultAdminFormValues(data.metadata));
    }

    setStatusMessage("Saved.");
  }

  return (
    <form className="admin-form" onSubmit={handleSubmit(submit)} noValidate>
      {statusMessage && (
        <Alert
          type="success"
          heading="Saved"
          headingLevel="h2"
          className="admin-form__alert"
        >
          {statusMessage}
        </Alert>
      )}

      {serverErrors.length > 0 && (
        <Alert
          type="error"
          heading="Could not save form"
          headingLevel="h2"
          className="admin-form__alert"
          validation
        >
          <ul>
            {serverErrors.map((message) => (
              <li key={message}>{message}</li>
            ))}
          </ul>
        </Alert>
      )}

      <div className="admin-form__fields">
        {formMetadata.fields.map((field) => {
          const registration = register(
            field.name,
            getClientValidationRules(field) as RegisterOptions<AdminFormValues>
          );

          return (
            <FormField
              key={field.name}
              field={field}
              error={errors[field.name] as FieldError | undefined}
              registration={registration}
            />
          );
        })}
      </div>

      <div className="admin-form__actions">
        <Button type="submit" disabled={isSubmitting}>
          {isSubmitting ? "Saving..." : "Save"}
        </Button>
        {cancelHref && (
          <a className="usa-button usa-button--outline" href={cancelHref}>
            {cancelLabel}
          </a>
        )}
      </div>
    </form>
  );
}
