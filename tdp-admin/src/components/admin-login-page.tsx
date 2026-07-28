import { GridContainer, Link } from "@trussworks/react-uswds";
import NextLink from "next/link";
import {
  getAuthBaseUrl,
  getBackendBaseUrl,
  getLoginUrl,
  getProviderLoginPath,
} from "@/lib/admin-auth";

export default function AdminLoginPage() {
  const backendBaseUrl = getBackendBaseUrl();
  const authBaseUrl = getAuthBaseUrl();
  const loginGovUrl = getLoginUrl("dotgov");
  const acfAmsUrl = getLoginUrl("ams");
  const loginGovPath = getProviderLoginPath("dotgov");
  const acfAmsPath = getProviderLoginPath("ams");
  const loginGovLogoSrc = "/login-gov-logo.svg";
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
                <NextLink href="/" aria-label="TANF Data Portal Home">
                  TANF Data Portal Admin
                </NextLink>
              </em>
            </div>
          </div>
        </header>

        <section className="usa-hero admin-hero" aria-label="Introduction">
          <GridContainer className="grid-container-widescreen admin-login-page__shell">
            <div className="usa-hero__callout admin-login-page__callout">
              <h1 className="usa-hero__heading">
                <span className="usa-hero__heading--alt font-serif-2xl margin-bottom-5">
                  Sign in to TANF Admin Page
                </span>
              </h1>
              <p className="text-black margin-bottom-5 admin-login-page__lede">
                Our vision is to build a secure, web-based reporting system that
                improves the federal reporting experience for TANF grantees and
                federal staff.
              </p>

              <div className="admin-login-page__actions">
                {loginGovUrl ? (
                  <Link href={loginGovPath} className="usa-button width-full sign-in-button" id="loginDotGovSignIn">
                    <div className="admin-login-page__login-button-content">
                      <span>Sign in with</span>
                      <img
                        src={loginGovLogoSrc}
                        alt="Login.gov"
                        className="admin-login-page__login-gov-logo"
                      />
                      <span>for grantees</span>
                    </div>
                  </Link>
                ) : (
                  <span className="usa-button usa-button--disabled width-full sign-in-button" aria-disabled="true" id="loginDotGovSignIn">
                    <div className="admin-login-page__login-button-content">
                      <span>Sign in with</span>
                      <img
                        src={loginGovLogoSrc}
                        alt="Login.gov"
                        className="admin-login-page__login-gov-logo"
                      />
                      <span>for grantees</span>
                    </div>
                  </span>
                )}

                {acfAmsUrl ? (
                  <Link href={acfAmsPath} className="usa-button width-full margin-top-3 sign-in-button" id="acfAmsSignIn">
                    Sign in with ACF AMS for ACF staff
                  </Link>
                ) : (
                  <span className="usa-button usa-button--disabled width-full margin-top-3 sign-in-button" aria-disabled="true" id="acfAmsSignIn">
                    Sign in with ACF AMS for ACF staff
                  </span>
                )}

                <Link href="/api/backend-health" className="usa-button usa-button--outline width-full margin-top-3">
                  Check backend health
                </Link>
              </div>

              <div className="admin-login-page__details">
                <p>
                  <strong>Configured auth base:</strong> {authBaseUrl ?? "Not configured"}
                </p>
                <p>
                  <strong>Configured backend:</strong> {backendBaseUrl ?? "Not configured"}
                </p>
              </div>
            </div>
          </GridContainer>
        </section>

        <section className="padding-top-4 usa-section admin-login-page__resources">
          <div className="grid-container-widescreen grid-row">
            <div className="desktop:padding-0 desktop:grid-col-3">
              <h2 className="resources-header font-heading-2xl margin-top-0 margin-bottom-0">
                Featured TANF Resources
              </h2>
              <div className="margin-top-1">
                <p>Questions about TANF data?</p>
                <p>
                  Email:{" "}
                  <a className="usa-link" href="mailto:tanfdata@acf.hhs.gov">
                    tanfdata@acf.hhs.gov
                  </a>
                </p>
              </div>
            </div>
            <div className="desktop:grid-col-9">
              <ul className="grid-row usa-card-group mobile:margin-0">
                <li className="usa-card--header-first padding-bottom-4 desktop:padding-right-2 desktop:grid-col-6 mobile:grid-col-12">
                  <div className="usa-card__container">
                    <header className="usa-card__header">
                      <h3 className="usa-card__heading">Need help with TDP?</h3>
                    </header>
                    <div className="usa-card__body">
                      <p>
                        The knowledge center contains resources on all things TDP
                        from account creation to data submission.
                      </p>
                    </div>
                    <div className="usa-card__footer">
                      <a
                        className="usa-button"
                        href="https://tdp-project-updates.app.cloud.gov/knowledge-center/"
                        target="_blank"
                        rel="noreferrer"
                      >
                        View Knowledge Center
                      </a>
                    </div>
                  </div>
                </li>
                <li className="usa-card--header-first padding-bottom-4 desktop:grid-col-6 mobile:grid-col-12">
                  <div className="usa-card__container">
                    <header className="usa-card__header">
                      <h3 className="usa-card__heading">Transmission File Layouts &amp; Edits</h3>
                    </header>
                    <div className="usa-card__body">
                      <p>
                        All transmission file layouts and edits for TANF and
                        SSP-MOE data reporting.
                      </p>
                    </div>
                    <div className="usa-card__footer">
                      <a
                        className="usa-button"
                        href="https://www.acf.hhs.gov/ofa/policy-guidance/final-tanf-ssp-moe-data-reporting-system-transmission-files-layouts-and-edits"
                        target="_blank"
                        rel="noreferrer"
                      >
                        View Layouts &amp; Edits
                      </a>
                    </div>
                  </div>
                </li>
                <li className="usa-card--header-first desktop:padding-right-2 desktop:padding-bottom-0 desktop:grid-col-6 mobile:grid-col-12 mobile:padding-bottom-4">
                  <div className="usa-card__container">
                    <header className="usa-card__header">
                      <h3 className="usa-card__heading">Tribal TANF Data Coding Instructions</h3>
                    </header>
                    <div className="usa-card__body">
                      <p>
                        File coding instructions addressing each data point that
                        Tribal TANF grantees are required to report upon.
                      </p>
                    </div>
                    <div className="usa-card__footer">
                      <a
                        className="usa-button"
                        href="https://acf.gov/sites/default/files/documents/ofa/tribal-tanf-data-report-instructions-valid-thru-2028-09.pdf"
                        target="_blank"
                        rel="noreferrer"
                      >
                        View Tribal TANF Coding Instructions
                      </a>
                    </div>
                  </div>
                </li>
                <li className="desktop:grid-col-6 mobile:grid-col-12">
                  <div className="usa-card__container">
                    <header className="usa-card__header">
                      <h3 className="usa-card__heading">ACF-199 and ACF-209 Instructions</h3>
                    </header>
                    <div className="usa-card__body">
                      <p>
                        Instructions and definitions for completion of forms
                        ACF-199 and ACF-209.
                      </p>
                    </div>
                    <div className="usa-card__footer">
                      <a
                        className="usa-button"
                        href="https://acf.gov/sites/default/files/documents/ofa/acf-199209-TANFSSP-data-report-instructions-valid-thru-2026-10.pdf"
                        target="_blank"
                        rel="noreferrer"
                      >
                        View ACF Form Instructions
                      </a>
                    </div>
                  </div>
                </li>
              </ul>
            </div>
          </div>
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
