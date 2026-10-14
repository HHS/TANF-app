import { forbidden, redirect } from "next/navigation";

export type AdminReadResult<T> =
  { ok: true; data: T } | { ok: false; status: number };

// Keep navigation outside the catch: Next.js implements redirects by throwing.
export async function readAdminResource<T>(
  request: () => Promise<Response>,
): Promise<AdminReadResult<T>> {
  let response: Response;
  try {
    response = await request();
  } catch {
    return { ok: false, status: 503 };
  }
  if (response.status === 401) redirect("/login");
  if (response.status === 403) forbidden();
  if (!response.ok) return { ok: false, status: response.status };
  try {
    return { ok: true, data: (await response.json()) as T };
  } catch {
    return { ok: false, status: 502 };
  }
}
