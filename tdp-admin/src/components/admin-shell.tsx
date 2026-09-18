import Image from "next/image";
import NextLink from "next/link";
import type { ReactNode } from "react";
import type { AdminSession } from "@/lib/admin-auth";
import AdminNavigation from "./admin-navigation";

function AdminGovBanner() {
  return (
    <section className="admin-gov-banner" aria-label="Official government website">
      <div className="grid-container-widescreen admin-gov-banner__inner">
        <p>A Demo website of the United States government</p>
        <p>Here&apos;s how you know</p>
      </div>
    </section>
  );
}

function AdminHeader({ session }: { session: AdminSession }) {
  const displayName =
    [session.user?.first_name, session.user?.last_name].filter(Boolean).join(" ") ||
    session.user?.email ||
    "Admin user";

  return (
    <header className="usa-header usa-header--extended admin-header">
      <div className="grid-container-widescreen admin-header__inner">
        <div className="usa-logo" id="extended-logo">
          <em className="usa-logo__text">
            <NextLink href="/dashboard" aria-label="TANF Data Portal Admin Home">
              TANF Data Portal Admin
            </NextLink>
          </em>
        </div>
        <div className="admin-header__account" aria-label="Admin account">
          <span className="admin-header__user">{displayName}</span>
          <a className="usa-button usa-button--outline" href="/logout">
            Sign out
          </a>
        </div>
      </div>
    </header>
  );
}

function AdminFooter() {
  const acfLogoSrc = "/ACFLogo.svg";

  return (
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
              <Image
                src={acfLogoSrc}
                alt="Administration for Children and Families, Office of Family Assistance"
                className="mobile-lg:maxw-mobile mobile:width-mobile"
                width={400}
                height={127}
              />
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}

export default function AdminShell({
  session,
  children,
}: {
  session: AdminSession;
  children: ReactNode;
}) {
  return (
    <>
      <a className="usa-skipnav" href="#main-content">
        Skip to main content
      </a>
      <div className="admin-app">
        <AdminGovBanner />
        <AdminHeader session={session} />
        <div className="grid-container-widescreen admin-app__body">
          <AdminNavigation roles={session.user?.roles} />
          <main className="admin-app__content" id="main-content">
            {children}
          </main>
        </div>
        <AdminFooter />
      </div>
    </>
  );
}
