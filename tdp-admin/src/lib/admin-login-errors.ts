export type AdminLoginSearchParams = {
  error?: string | string[];
  message?: string | string[];
};

function firstSearchParamValue(value?: string | string[]) {
  return Array.isArray(value) ? value[0] : value;
}

export function getAdminLoginErrorMessage(
  searchParams?: AdminLoginSearchParams
) {
  const error = firstSearchParamValue(searchParams?.error);

  if (error === "admin_login_failed") {
    return (
      firstSearchParamValue(searchParams?.message) ??
      "Your account could not be signed in."
    );
  }

  if (error === "admin_login_validation") {
    return (
      firstSearchParamValue(searchParams?.message) ??
      "Your account could not be signed in."
    );
  }

  return "";
}
