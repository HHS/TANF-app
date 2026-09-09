import { headers } from "next/headers";
import { forbidden, redirect } from "next/navigation";
import { GridContainer } from "@trussworks/react-uswds";
import NextLink from "next/link";
import { checkAdminSession } from "@/lib/admin-auth";

export default async function AdminHomePage() {
  const requestHeaders = await headers();
  const cookieHeader = requestHeaders.get("cookie");
  const session = await checkAdminSession(cookieHeader);

  if (!session.authenticated) {
    redirect("/login");
  }

  if (session.authorized !== true) {
    forbidden();
  }

  const displayName =
    [session.user?.first_name, session.user?.last_name].filter(Boolean).join(" ") ||
    session.user?.email ||
    "Admin user";
  const roles = session.user?.roles?.length
    ? session.user.roles.join(", ")
    : "No roles returned";
  const sessionStatus = "Authenticated and admin-authorized";
  const statusDetail =
    session.detail ??
    "Django validated your admin session and authorized this view.";
  const acfLogoSrc = "/ACFLogo.svg";

  return (
    <>
      <a className="usa-skipnav" href="#main-content">
        Skip to main content
      </a>
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

        <section className="admin-success" aria-label="Admin login success">
          <GridContainer className="grid-container-widescreen admin-success__shell">
            <div className="admin-success__panel">
              <p className="admin-console__eyebrow">Login successful</p>
              <h1>Welcome to the admin console</h1>
              <p className="admin-success__lede">
                {statusDetail}
              </p>

              <dl className="admin-success__details">
                <div>
                  <dt>User</dt>
                  <dd>{displayName}</dd>
                </div>
                <div>
                  <dt>Email</dt>
                  <dd>{session.user?.email ?? "Not returned"}</dd>
                </div>
                <div>
                  <dt>Roles</dt>
                  <dd>{roles}</dd>
                </div>
                <div>
                  <dt>Session</dt>
                  <dd>{sessionStatus}</dd>
                </div>
              </dl>

              <div className="admin-success__actions">
                <a className="usa-button" href="/api/backend-health">
                  Check backend health
                </a>
                <a className="usa-button usa-button--outline" href="/api-validation">
                  Validate API response
                </a>
                <a className="usa-button usa-button--outline" href="/logout">
                  Sign out
                </a>
              </div>
            </div>
          </GridContainer>
        </section>

        <footer className="usa-footer usa-footer--slim admin-footer">
          <div className="usa-footer__primary-section">
            <div className="grid-container-widescreen grid-row">
              <div className="mobile-lg:grid-col-8">
                <nav className="usa-footer__nav" aria-label="Footer navigation">
                  <ul className="grid-row grid-gap">
                    <li className="mobile-lg:grid-col-6 desktop:grid-col-auto usa-footer__primary-content">
                      <a
                        className="usa-footer__primary-link"
                        href="https://tdp-project-updates.app.cloud.gov/knowledge-center/"
                        target="_blank"
                        rel="noreferrer"
                      >
                        Knowledge Center
                      </a>
                    </li>
                    <li className="mobile-lg:grid-col-6 desktop:grid-col-auto usa-footer__primary-content">
                      <a
                        className="usa-footer__primary-link"
                        href="https://www.acf.hhs.gov/privacy-policy"
                        target="_blank"
                        rel="noreferrer"
                      >
                        Privacy Policy
                      </a>
                    </li>
                    <li className="mobile-lg:grid-col-6 desktop:grid-col-auto usa-footer__primary-content">
                      <a
                        className="usa-footer__primary-link"
                        href="https://www.hhs.gov/vulnerability-disclosure-policy/index.html"
                        target="_blank"
                        rel="noreferrer"
                      >
                        Vulnerability Disclosure Policy
                      </a>
                    </li>
                  </ul>
                </nav>
              </div>
            </div>
          </div>
          <div className="usa-footer__secondary-section">
            <div className="grid-container-widescreen">
              <div className="usa-footer__logo margin-left-neg-205">
                <div className="grid-col-auto">
                  <img
                    src={acfLogoSrc}
                    alt="Administration for Children and Families, Office of Family Assistance"
                    className="mobile-lg:maxw-mobile mobile:width-mobile"
                  />
                </div>
              </div>
            </div>
          </div>
        </footer>
      </main>
    </>
  );
}
