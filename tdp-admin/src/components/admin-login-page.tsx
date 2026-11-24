import { GridContainer, Link } from "@trussworks/react-uswds";
import {
  getAdminLoginUrl,
  getAdminProviderLoginPath,
  checkBackendHealth,
} from "@/lib/admin-auth";

type AdminLoginPageProps = {
  loginErrorMessage?: string;
};

export default async function AdminLoginPage({
  loginErrorMessage = "",
}: AdminLoginPageProps) {
  const backendHealth = await checkBackendHealth();
  const loginGovUrl = getAdminLoginUrl("dotgov");
  const acfAmsUrl = getAdminLoginUrl("ams");
  const loginGovPath = getAdminProviderLoginPath("dotgov");
  const acfAmsPath = getAdminProviderLoginPath("ams");
  const loginGovLogoSrc = "/login-gov-logo.svg";
  const acfLogoSrc = "/ACFLogo.svg";

  return (
    <>
        <section className="usa-hero admin-hero" aria-label="Introduction">
          <GridContainer className="grid-container-widescreen admin-login-page__shell">
            <div className="usa-hero__callout admin-login-page__callout">
              <h1 className="usa-hero__heading">
                <span className="usa-hero__heading--alt">
                  Sign in to TANF Admin
                </span>
              </h1>
              <p className="admin-login-page__lede">
                Manage user accounts and support TANF reporting. Choose your
                sign-in provider to continue.
              </p>

              {loginErrorMessage && (
                <div
                  className="usa-alert usa-alert--error admin-login-page__alert"
                  role="alert"
                >
                  <div className="usa-alert__body">
                    <h2 className="usa-alert__heading">Could not sign in</h2>
                    <p className="usa-alert__text">{loginErrorMessage}</p>
                  </div>
                </div>
              )}

              <div className="admin-login-page__actions">
                {loginGovUrl ? (
                  <Link
                    href={loginGovPath}
                    className="usa-button width-full sign-in-button"
                    aria-disabled="false"
                    id="loginDotGovSignIn"
                  >
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
                  <span
                    className="usa-button usa-button--disabled width-full sign-in-button"
                    aria-disabled="true"
                    id="loginDotGovSignIn"
                  >
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
                  <Link
                    href={acfAmsPath}
                    className="usa-button width-full margin-top-3 sign-in-button"
                    aria-disabled="false"
                    id="acfAmsSignIn"
                  >
                    Sign in with ACF AMS for ACF staff
                  </Link>
                ) : (
                  <span
                    className="usa-button usa-button--disabled width-full margin-top-3 sign-in-button"
                    aria-disabled="true"
                    id="acfAmsSignIn"
                  >
                    Sign in with ACF AMS for ACF staff
                  </span>
                )}

              </div>

              {!backendHealth.ok && (
                <div className="admin-login-page__details" role="status">
                  <p>
                    Sign-in services may be temporarily unavailable. If you cannot
                    sign in, try again later or contact{" "}
                    <a className="admin-login-page__inline-link" href="mailto:tanfdata@acf.hhs.gov">
                      tanfdata@acf.hhs.gov
                    </a>.
                  </p>
                </div>
              )}
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
    </>
  );
}
