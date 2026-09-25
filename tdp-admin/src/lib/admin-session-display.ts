import type { AdminRole } from "./admin-auth";

function getRoleLabel(role: AdminRole) {
  if (typeof role === "string") {
    return role;
  }

  return role.name ?? String(role.id ?? "").trim();
}

export function getAdminRoleSummary(roles?: AdminRole[]) {
  const labels =
    roles
      ?.map(getRoleLabel)
      .map((role) => role.trim())
      .filter(Boolean) ?? [];

  return labels.length ? labels.join(", ") : "No roles returned";
}

