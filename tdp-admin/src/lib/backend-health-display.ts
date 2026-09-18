import type { BackendHealth } from "./admin-auth";

export function getBackendHealthSummary(health: BackendHealth) {
  const status = [health.status, health.statusText].filter(Boolean).join(" ");

  if (health.ok) {
    return status ? `Reachable (${status})` : "Reachable";
  }

  if (health.status) {
    return status ? `Responding (${status})` : `Responding (${health.status})`;
  }

  return health.error ? `Unavailable (${health.error})` : "Unavailable";
}

