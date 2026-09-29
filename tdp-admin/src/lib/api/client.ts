import {
  buildAdminRequestHeaders,
  getAdminBackendBaseUrl,
  setInternalBackendForwardedProto,
} from "../admin-auth";

const MUTATING_METHODS = new Set(["POST", "PUT", "PATCH", "DELETE"]);
const BODYLESS_METHODS = new Set(["GET", "HEAD"]);

const PROVENANCE_HEADER_NAMES = [
  "x-request-id",
  "x-correlation-id",
  "x-forwarded-for",
  "x-real-ip",
  "cf-connecting-ip",
  "x-forwarded-host",
  "x-forwarded-proto",
  "user-agent",
  "referer",
  "origin",
  "x-keycloak-client",
  "x-auth-flow",
];

type HeaderGetter = {
  get(name: string): string | null;
};

export type AdminApiRequestOptions = {
  method?: string;
  search?: string;
  trailingSlash?: boolean;
  body?: BodyInit | null;
  cookieHeader?: string | null;
  csrfToken?: string | null;
  incomingHeaders?: HeaderGetter;
  headers?: HeadersInit;
  sourceRoute?: string;
  requestId?: string | null;
};

export type ReadAdminResourceOptions = Omit<
  AdminApiRequestOptions,
  "method" | "body"
>;

export function isMutatingAdminApiMethod(method = "GET") {
  return MUTATING_METHODS.has(method.toUpperCase());
}

export function getAdminApiUrl(
  pathSegments: string[],
  search = "",
  trailingSlash = false
) {
  const backendBaseUrl = getAdminBackendBaseUrl();

  if (!backendBaseUrl) {
    return null;
  }

  const normalizedBaseUrl = backendBaseUrl.replace(/\/$/, "");
  const normalizedPath = pathSegments.map(encodeURIComponent).join("/");
  return `${normalizedBaseUrl}/${normalizedPath}${trailingSlash ? "/" : ""}${search}`;
}

export function setAuthenticatedNoStore(headers: Headers) {
  headers.set("Cache-Control", "no-store");
  headers.set("Pragma", "no-cache");
  headers.set("Expires", "0");
  return headers;
}

function forwardProvenanceHeaders(
  requestHeaders: Headers,
  incomingHeaders?: HeaderGetter
) {
  for (const headerName of PROVENANCE_HEADER_NAMES) {
    const value = incomingHeaders?.get(headerName);
    if (value && !requestHeaders.has(headerName)) {
      requestHeaders.set(headerName, value);
    }
  }

  return requestHeaders;
}

export async function requestAdminApi(
  pathSegments: string[],
  {
    method = "GET",
    search = "",
    trailingSlash = false,
    body,
    cookieHeader,
    csrfToken,
    incomingHeaders,
    headers = {},
    sourceRoute,
    requestId,
  }: AdminApiRequestOptions = {}
) {
  const url = getAdminApiUrl(pathSegments, search, trailingSlash);

  if (!url) {
    throw new Error(
      "ADMIN_BACKEND_URL or NEXT_PUBLIC_BACKEND_URL is not configured."
    );
  }

  const adminProxyToken = process.env.ADMIN_API_PROXY_TOKEN;

  if (!adminProxyToken) {
    throw new Error("ADMIN_API_PROXY_TOKEN is not configured.");
  }

  const normalizedMethod = method.toUpperCase();
  const requestHeaders = buildAdminRequestHeaders({
    cookieHeader,
    csrfToken,
    includeCsrf: isMutatingAdminApiMethod(normalizedMethod),
    headers,
  });
  forwardProvenanceHeaders(requestHeaders, incomingHeaders);
  setInternalBackendForwardedProto(url, requestHeaders);
  requestHeaders.set("X-Admin-Proxy-Token", adminProxyToken);
  requestHeaders.set(
    "X-Request-ID",
    requestId || requestHeaders.get("X-Request-ID") || crypto.randomUUID()
  );

  if (sourceRoute) {
    requestHeaders.set("X-TDP-Admin-Source-Route", sourceRoute);
  }

  return fetch(url, {
    method: normalizedMethod,
    credentials: "include",
    cache: "no-store",
    redirect: "manual",
    headers: requestHeaders,
    body: BODYLESS_METHODS.has(normalizedMethod) ? undefined : body,
  });
}
