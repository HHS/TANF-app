import { headers } from "next/headers";
import { forbidden, redirect } from "next/navigation";
import { GridContainer } from "@trussworks/react-uswds";
import NextLink from "next/link";
import { requestAdminApi, setAuthenticatedNoStore } from "@/lib/admin-api";
import { checkAdminSession } from "@/lib/admin-auth";

export const dynamic = "force-dynamic";

function toPathSegments(endpoint: string) {
  return endpoint
    .split("/")
    .map((segment) => segment.trim())
    .filter(Boolean);
}

async function fetchValidationResponse({
  endpoint,
  cookieHeader,
  incomingHeaders,
}: {
  endpoint: string;
  cookieHeader: string | null;
  incomingHeaders: Awaited<ReturnType<typeof headers>>;
}) {
  const response = await requestAdminApi(toPathSegments(endpoint), {
    method: "GET",
    cookieHeader,
    incomingHeaders,
    sourceRoute: "/api-validation",
  });
  const body = await response.text();

  return {
    status: response.status,
    statusText: response.statusText,
    cacheControl: setAuthenticatedNoStore(new Headers(response.headers)).get(
      "Cache-Control"
    ),
    contentType: response.headers.get("content-type") ?? "Not returned",
    body,
  };
}

export default async function ApiValidationPage({
  searchParams,
}: {
  searchParams: Promise<{ endpoint?: string }>;
}) {
  const requestHeaders = await headers();
  const cookieHeader = requestHeaders.get("cookie");
  const session = await checkAdminSession(cookieHeader);

  if (!session.authenticated) {
    redirect("/login");
  }

  if (session.authorized !== true) {
    forbidden();
  }

  const params = await searchParams;
  const endpoint = params.endpoint ?? "auth_check";
  const validation = await fetchValidationResponse({
    endpoint,
    cookieHeader,
    incomingHeaders: requestHeaders,
  }).catch((err) => ({
    status: 500,
    statusText: "Validation request failed",
    cacheControl: "no-store",
    contentType: "Not returned",
    body: err instanceof Error ? err.message : String(err),
  }));

  return (
    <main className="admin-login-page" id="main-content">
      <section className="admin-gov-banner" aria-label="Official government website">
        <div className="grid-container-widescreen admin-gov-banner__inner">
          <p>A Demo website of the United States government</p>
          <p>Here&apos;s how you know</p>
        </div>
      </section>

      <header className="usa-header usa-header--extended admin-header">
        <div className="grid-container-widescreen usa-nav__wide desktop:padding-left-4 desktop:border-bottom-0 mobile:border-bottom-1px mobile:padding-left-0 mobile:padding-right-0">
          <div className="usa-logo" id="extended-logo">
            <em className="usa-logo__text">
              <NextLink href="/" aria-label="TANF Data Portal Admin Home">
                TANF Data Portal Admin
              </NextLink>
            </em>
          </div>
        </div>
      </header>

      <section className="admin-success" aria-label="API response validation">
        <GridContainer className="grid-container-widescreen admin-success__shell">
          <div className="admin-success__panel">
            <p className="admin-console__eyebrow">API validation</p>
            <h1>Django API response validation</h1>
            <p className="admin-success__lede">
              This page calls one Django endpoint through the shared admin API helper and
              displays the response returned by Django.
            </p>

            <dl className="admin-success__details">
              <div>
                <dt>Endpoint</dt>
                <dd>{endpoint}</dd>
              </div>
              <div>
                <dt>Status</dt>
                <dd>
                  {validation.status} {validation.statusText}
                </dd>
              </div>
              <div>
                <dt>Cache-Control</dt>
                <dd>{validation.cacheControl}</dd>
              </div>
              <div>
                <dt>Content-Type</dt>
                <dd>{validation.contentType}</dd>
              </div>
            </dl>

            <pre className="admin-api-validation__body">{validation.body}</pre>
          </div>
        </GridContainer>
      </section>
    </main>
  );
}
